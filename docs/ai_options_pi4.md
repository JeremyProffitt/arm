# AI options for LUMA on Raspberry Pi 4 (8 GB)

Checked against primary sources on 8 September 2026. This is a design study, not a record of tests on assembled hardware.

## Recommendation

Keep motion control deterministic and add AI in stages:

1. Start with CPU-only voice. Use a USB microphone, local wake-word detection, streaming speech recognition, and the existing `espeak-ng` output. Map a small set of spoken intents to existing scenes. This is enough for commands such as “look at me”, “say hi”, “wink”, “stop”, and “light on”.
2. Add the **$70 Raspberry Pi AI Camera** on CSI when vision is wanted. It is the best-supported Pi 4 vision option. It performs inference in the sensor and has official Pi 4 object-detection and pose examples.
3. Add a small local language model only for conversation and intent proposals. Start with Qwen3 0.6B or 1.7B in a 4-bit GGUF file through `llama.cpp`. Do not put it in the motor-control path.
4. Buy a USB accelerator only for a measured need. Choose an OAK camera when near-field depth is required. Choose Coral only when a known Edge-TPU model and a separate legacy runtime are acceptable.

No well-supported Pi 4 plug-in currently accelerates both vision and a local language model. The official Hailo boards require Raspberry Pi 5. ASUS UGen300 is an interesting USB language-and-vision accelerator, but ASUS does not document Raspberry Pi 4 or Raspberry Pi OS support. It should be treated as an evaluation device, not a purchase recommendation.

## What the Pi 4 can do without an accelerator

| Workload | Practical software | Pi 4 use |
| --- | --- | --- |
| Object detection | Picamera2, OpenCV, and LiteRT with a quantized MobileNet-class model | Good for a proof of concept at reduced input size and a limited frame rate. Raspberry Pi maintains a current [Picamera2 LiteRT example](https://github.com/raspberrypi/picamera2/blob/main/examples/tensorflow/real_time.py). Reserve full-rate vision for a camera accelerator. |
| Pose and hand gesture | LiteRT or MediaPipe Tasks on sampled frames | Feasible, but it competes with speech and the language model for the four CPU cores. MediaPipe exposes live-stream [pose](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarker) and [gesture](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/GestureRecognizer) tasks. Verify an ARM64 wheel on the exact Raspberry Pi OS image before selecting it. |
| Wake word | `openWakeWord`, or `sherpa-onnx` keyword spotting | Light enough to run continuously. `openWakeWord` reports that one Raspberry Pi 3 core can run 15–20 models in real time and supports Arm64 Linux noise suppression; use only one tuned wake phrase for LUMA. See the [official repository](https://github.com/dscripka/openWakeWord). |
| Speech recognition | `sherpa-onnx` streaming Zipformer; `whisper.cpp` tiny/base for utterances | `sherpa-onnx` has current Linux AArch64 packages and documents its streaming models as real-time on Pi 4. It also supplies keyword spotting, voice-activity detection, and TTS in one runtime. See its [platform list](https://github.com/k2-fsa/sherpa-onnx), [Pi 4 model guidance](https://k2-fsa.github.io/sherpa/onnx/pretrained_models/small-online-models.html), and [CPU installation](https://k2-fsa.github.io/sherpa/onnx/python/install.html). `whisper.cpp` officially supports Raspberry Pi; its tiny and base models use about 273 MB and 388 MB respectively and can be quantized. See the [`whisper.cpp` README](https://github.com/ggml-org/whisper.cpp). |
| Speech synthesis | Existing `espeak-ng`; Piper for a more natural voice | Keep `espeak-ng` as the low-load fallback. Current Piper supplies an Arm64 Raspberry Pi 4 binary and a persistent server so the model need not reload for each sentence. Piper is GPL-3.0. See the [Piper project](https://github.com/OHF-Voice/piper1-gpl) and [Pi 4 CLI notes](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md). |
| Local language model | `llama.cpp`; Ollama for easier model management | Use a small model and a short context. `llama.cpp` supports ARM CPU inference, 2–8-bit quantization, a local API server, and grammar-constrained JSON. Qwen publishes 0.6B and 1.7B Qwen3 models under Apache 2.0 and supports `llama.cpp` and Ollama. See [`llama.cpp`](https://github.com/ggml-org/llama.cpp), [Qwen3](https://github.com/QwenLM/Qwen3), and the [Ollama Arm64 package](https://docs.ollama.com/linux). |

Engineering judgment: a 0.6B or 1.7B 4-bit model is the sensible starting range while audio and control remain live. A 4B 4-bit model may fit in 8 GB, but latency and memory pressure must be measured. A 7B model is not a practical default for simultaneous vision, speech, face rendering, and motion control. Disable Qwen “thinking” mode for short robot commands. Limit model threads and context so the controller always has CPU time.

Vosk is small, but its current official installation page still limits Python to 3.5–3.9. That conflicts with LUMA’s Python 3.11 baseline, so it is not the first choice despite official Raspberry Pi support. See the [Vosk installation page](https://alphacephei.com/vosk/install) and [model sizes](https://alphacephei.com/vosk/models).

## Add-on comparison

| Option | Performance and runtime | Pi 4 and LUMA integration | Power, heat, size, and price |
| --- | --- | --- | --- |
| **Raspberry Pi AI Camera** | Sony IMX500 runs its own image stream. Official packages include MobileNet SSD and PoseNet, with Picamera2 examples for detection, pose, classification, segmentation, and custom packaged models. Input tensors are at most 640 × 640 INT8/UINT8. Raspberry Pi does not publish a TOPS rating. See the [AI Camera documentation](https://www.raspberrypi.com/documentation/accessories/ai-camera.html). | Explicitly supported on Pi 4 over CSI. It leaves USB and the Pi CPU available. It does not accelerate audio, an LLM, or arbitrary host tensors. It can coexist electrically with either LUMA display because CSI is separate from USB and DSI. | 25 × 24 × 11.9 mm, 6 g, 0–50 °C, supplied cable 200 mm, official list price **$70**. See the [product brief](https://datasheets.raspberrypi.com/camera/ai-camera-product-brief.pdf) and [product page](https://www.raspberrypi.com/products/ai-camera/). |
| **Luxonis OAK-D Short Range** | RVC2 provides 4 TOPS total and 1.4 TOPS for neural inference. It runs converted models, cameras, tracking, encoding, and stereo processing on the device through current DepthAI software. Its stated ideal depth range is 30 cm–1 m, which fits a desk companion. See the [RVC2 specification](https://docs.luxonis.com/hardware/platform/rvc/rvc2) and [DepthAI neural-network support](https://docs.luxonis.com/software-v3/depthai/depthai-components/nodes/neural_network). | Works as a USB 2/3 peripheral; Luxonis provides Raspberry Pi deployment instructions and AArch64 wheels. It brings its own cameras. Mount it on the fixed pedestal or desk, not the moving head. It is the best choice when real depth is more important than minimum cost. | 56 × 36 × 25.5 mm and 72 g. RVC2 cameras use about 2.5–3 W for streaming, plus up to 1 W for AI, 0.5 W for stereo, and 0.5 W for encoding. Current official price is **$229**. See the [OAK-D Short Range shop page](https://shop.luxonis.com/products/oak-d-sr) and [USB power guidance](https://docs.luxonis.com/hardware/platform/deploy/usb-deployment-guide/). Use a powered USB 3 hub. |
| **Coral USB Accelerator** | 4 TOPS INT8 at 2 W, over USB 3. It accepts only fully 8-bit TensorFlow Lite models compiled for Edge TPU; unsupported operations fall back to the host CPU. See the [datasheet](https://coral.ai/static/files/Coral-USB-Accelerator-datasheet.pdf) and [model rules](https://coral.ai/docs/edgetpu/models-intro/). | Google explicitly lists Pi 4. However, its official guide requires Python 3.6–3.9, while LUMA requires 3.11+. The [PyCoral](https://github.com/google-coral/pycoral) and [libedgetpu](https://github.com/google-coral/libedgetpu) repositories were archived in 2025. Use a separate Python 3.9 process or the C++ API and freeze the image. This is a fixed-function vision option, not an LLM accelerator. | 65 × 30 × 8 mm. It needs at least 500 mA at 5 V and can peak near 900 mA at maximum clock. Maximum-clock mode consumes more power and can make the metal case burn-hot; use reduced clock and ventilation. Google no longer publishes a current first-party price. See the [official setup guide](https://coral.ai/docs/accelerator/get-started/). |
| **ReSpeaker XVF3800 USB 4-Mic Array** | This is an audio front-end, not a general neural accelerator. Its XMOS processor performs acoustic echo cancellation, gain control, voice-activity detection, direction finding, beamforming, noise suppression, and dereverberation before audio reaches the Pi. | Official USB firmware is plug-and-play on Raspberry Pi OS. It improves far-field speech while reducing Pi audio work. Prefer the enclosed USB model and evaluate using its audio output in place of the current USB speaker, so echo cancellation has a playback reference and one USB device can replace two. | Four microphones, stated pickup to 5 m. Current enclosed-model price is **$62.99**. See the [setup guide](https://wiki.seeedstudio.com/respeaker_xvf3800_introduction/) and [official shop page](https://www.seeedstudio.com/ReSpeaker-XVF3800-USB-4-Mic-Array-With-Case-p-6490.html). |
| **ASUS UGen300 USB** | Hailo-10H, 40 TOPS INT4 or 20 TOPS INT8, 8 GB LPDDR4, with vendor claims for vision, LLM, VLM, and Whisper workloads. Hailo models use HailoRT and compiled HEF files. | ASUS lists ARM Linux and SBC use, but does not list Pi 4 or Raspberry Pi OS. Its USB 3.1 Gen 2 link is 10 Gbit/s; Pi 4 USB 3 is limited to 5 Gbit/s. Driver behavior and performance at the reduced link are unverified. Obtain vendor confirmation or a returnable evaluation unit before purchase. | 105 × 50 × 18 mm, 150 g, 2.5 W typical. No first-party US price was found. See the [ASUS announcement](https://press.asus.com/news/press-releases/asus-ugen300-usb-ai-accelerator-generative-ai-edge/), [technical specification](https://www.asus.com/ca-en/motherboards-components/ai-accelerator/ugen/ugen300-usb-8g/techspec/), and [official utility](https://github.com/Asus-UGen-Series/Ugen-Utility). |

## Options that do not fit this Pi 4

- Raspberry Pi AI Kit, AI HAT+, and AI HAT+ 2 require the exposed PCIe connector on Raspberry Pi 5. A standard Pi 4 Model B does not expose PCIe, so an M.2 HAT, raw Hailo module, or USB NVMe enclosure cannot make these products work. The current HATs provide 13 or 26 TOPS for vision; AI HAT+ 2 provides 40 TOPS and 8 GB accelerator RAM for LLMs, but it is a **Pi 5 platform change**, not a Pi 4 add-on. See the [AI HAT hardware requirements](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html), [AI HAT+ product](https://www.raspberrypi.com/products/ai-hat/), and [AI HAT+ 2 product](https://www.raspberrypi.com/products/ai-hat-plus-2/).
- Do not buy an Intel Neural Compute Stick 2 for a new build. Intel ended shipments in 2022, technical support in 2023, and warranty support in 2024. NCS2 is held on OpenVINO 2022.3 LTS. See Intel’s [end-of-life notice](https://www.intel.com/content/www/us/en/support/articles/000090446/boards-and-kits/neural-compute-sticks.html) and [OpenVINO support notice](https://www.intel.com/content/www/us/en/support/articles/000093181/boards-and-kits.html).

## Interface, power, and physical limits

The Pi 4 has two USB 3 ports and two USB 2 ports, with only **1.2 A total** available to all USB peripherals. LUMA already assigns USB to the ESP32-S3 face and speaker. A microphone plus a Coral or OAK device can fill all four physical ports and exceed the power budget. Use a quality externally powered USB 3 hub for any USB accelerator or OAK camera. A powered hub adds power and ports; it does not add Pi host bandwidth. See the [Raspberry Pi USB limits](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#universal-serial-bus-usb) and LUMA’s existing [electrical architecture](../electronics/architecture.md).

The following combinations need explicit treatment:

- AI Camera plus the standard USB face and USB audio is electrically compatible. The camera uses CSI.
- AI Camera plus the optional DSI face is also electrically compatible. CSI and DSI are separate. The mechanical cable route is not solved.
- OAK plus Coral is technically possible through separate USB ports, but the accelerators do not pool memory or compute. They run separate model formats and runtimes, consume the same limited USB power and bandwidth, and are redundant for this project.
- No Pi 5 AI HAT, AI Kit, or M.2 accelerator can be combined with the standard Pi 4 Model B.
- The supplied AI Camera cable is 200 mm. LUMA has no camera mount or moving CSI harness. A camera on the head would require new printed parts, a longer flex cable, bend and strain-relief validation through every joint, and a new head-mass and torque check. A fixed pedestal camera is the low-risk first build.
- Place Coral, a powered hub, or an ASUS evaluation unit in a ventilated fixed location. Do not add their mass or stiff cables to the wrist. The OAK-D Short Range is also best fixed to the base or desk.

Sustained CPU inference needs active airflow. Raspberry Pi states that Pi 4 progressively throttles its Arm cores from 80–85 °C and recommends a fan for best sustained performance. LUMA already calls for a heatsink and ventilation; add a fan only after checking GPIO conflicts and measuring the closed pedestal. See the [official thermal guidance](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#frequency-management-and-thermal-control).

## Safe control boundary

AI output must be advice to the existing controller, never a servo command:

```text
microphone -> wake word -> speech text ----+
                                             +-> intent proposal -> allowlist -> LUMA controller
camera ----> object/pose/gesture events ----+                         |
                                                                      +-> existing arming, limits, faults, PCA9685
```

The allowlist should accept a few high-level intents with a confidence threshold, freshness limit, rate limit, and timeout. It should reject unknown text and stale perception. The LLM must not write `config.json`, set `calibrated=true`, arm the mechanism, clear a fault, select pulse widths, or bypass the range checks. Loss of the AI process must leave the deterministic controller operating or holding safely.

Keep the independent motor-power stop. LUMA’s five VL53L1X sectors and any camera inference are not safety-rated and do not cover every pinch point. The servos have no readable position, current, or temperature. A software fault can leave the PCA9685 at its last pulse widths, so unexpected motion still requires the physical motor stop. These limits and the first-motion procedure are already recorded in [electronics/architecture.md](../electronics/architecture.md) and [software/README.md](../software/README.md).

## Proof before the next stage

For each stage, record on the actual 8 GB Pi 4:

- wake false-accept and false-reject counts in the intended room;
- median and 95th-percentile speech and intent latency;
- camera inference rate, end-to-end event latency, and false detections;
- CPU and memory use while face, audio, sensors, and one scene run together;
- `vcgencmd measure_temp` and `vcgencmd get_throttled` before and after a 30-minute sustained test;
- USB disconnects, undervoltage reports, and hub behavior under peak load;
- behavior when the microphone, camera, model process, display, sensor, or PCA9685 is unplugged;
- confirmation that no AI event can arm, clear a latched fault, or generate raw motor output.

Advance only when the current stage meets a written latency target without throttling, undervoltage, dropped safety polling, or unexpected motion.

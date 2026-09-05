"""Read selected small vendor source files from the remote ZIP using HTTP ranges.

This development tool never executes downloaded source and avoids downloading
the package's large speech assets. Sources retain their vendor ownership.
"""
import io
import urllib.request
import zipfile
from pathlib import Path

URL = "https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.85/ESP32-S3-Touch-LCD-1.85-Demo.zip"


class HTTPRange(io.RawIOBase):
    def __init__(self,url):
        self.url=url
        with urllib.request.urlopen(urllib.request.Request(url,method="HEAD"),timeout=30) as r:
            self.length=int(r.headers["Content-Length"])
        self.pos=0
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.length+offset
        return self.pos
    def read(self,size=-1):
        size=self.length-self.pos if size<0 else min(size,self.length-self.pos)
        if size<=0: return b""
        req=urllib.request.Request(self.url,headers={"Range":f"bytes={self.pos}-{self.pos+size-1}"})
        with urllib.request.urlopen(req,timeout=30) as r:
            if r.status !=206:
                raise RuntimeError("Server did not honor range request")
            data=r.read()
        self.pos+=len(data)
        return data


if __name__=="__main__":
    target=Path(__file__).parent/"vendor"/"display_reference"
    target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(HTTPRange(URL)) as archive:
        for info in archive.infolist():
            name=info.filename
            if name.endswith((".c",".cpp",".h",".ino")) and any(token in name.lower() for token in
                ("lcd_driver","display_driver","st77916","i2c_driver","tca9554")) and "Arduino/" in name:
                print(name,info.file_size,flush=True)
                if info.file_size<200000 and not (target/Path(name).name).exists():
                    (target/Path(name).name).write_bytes(archive.read(info))

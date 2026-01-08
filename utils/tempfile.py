import tempfile
import os

class TempFile:
    def __init__(self, mode='w+', suffix='', prefix='tmp', dir=None):
        """创建临时文件对象"""
        self._temp = tempfile.NamedTemporaryFile(
            mode=mode,
            delete=False,  # 不自动删除
            suffix=suffix,
            prefix=prefix,
            dir=dir
        )
        self.path = self._temp.name
        self._closed = False
    
    def write(self, data):
        """写入数据"""
        if not self._closed:
            self._temp.write(data)
            self._temp.flush()
        else:
            raise ValueError("文件已关闭")

    def writeline(self, line):
        """写入一行（自动添加换行符）"""
        if not line.endswith('\n'):
            line += '\n'
        self.write(line)
    
    def read(self):
        """读取数据"""
        if not self._closed:
            self._temp.seek(0)
            return self._temp.read()
        else:
            # 文件已关闭，重新打开读取
            with open(self.path, 'r') as f:
                return f.read()
    
    def close(self):
        """关闭文件"""
        if not self._closed:
            self._temp.close()
            self._closed = True
    
    def delete(self):
        """删除文件"""
        if not self._closed:
            self.close()
        if os.path.exists(self.path):
            os.unlink(self.path)
    
    def __repr__(self):
        return f"TempFile(path='{self.path}')"
from collections.abc import Generator
from typing import Any
import requests
import io
import zipfile

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ZipLinkGetImgTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        zip_link = tool_parameters.get("zip_link")
         # 下载zip文件到内存
        response = requests.get(zip_link)
        response.raise_for_status()
        # 直接从内存中读取zip文件
        zip_data = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            # 获取所有文件名
            file_list = zip_ref.namelist()
            # 筛选出images文件夹中的文件
            image_files = [f for f in file_list if f.startswith('images/') and not f.endswith('/')]
            # 提取每个图片文件并转换为data URL格式
            yield self.create_text_message(f"Found {len(image_files)} image files in the zip file.")
            for image_file in image_files:
                with zip_ref.open(image_file) as img_file:
                    # 读取图片数据
                    yield self.create_blob_message(
                        blob=img_file.read(), 
                        meta={
                            "mime_type": "image/png",
                            "filename": image_file
                        }
                    )

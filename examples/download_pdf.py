from zoteroapi import ZoteroLocal
from pathlib import Path
from typing import Optional, Dict

def get_pdf_attachment_key(item: Dict) -> Optional[str]:
    """
    从条目中获取PDF附件的key
    
    Args:
        item: Zotero条目数据
        
    Returns:
        PDF附件的key，如果没有PDF附件则返回None
    """
    links = item.get('links', {})
    attachment = links.get('attachment', {})
    
    if (attachment and 
        attachment.get('attachmentType') == 'application/pdf'):
        # 从href中提取key
        href = attachment.get('href', '')
        # print(f"href: {href}")
        return href.split('/')[-1]
    
    return None

def download_item_pdf(client: ZoteroLocal, 
                     item_key: str, 
                     output_dir: str = "downloads") -> None:
    """
    下载指定条目的PDF文件
    
    Args:
        client: ZoteroLocal实例
        item_key: 条目的key
        output_dir: 输出目录
    """
    try:
        # 获取条目信息
        item = client.get_item_by_key(item_key)
        
        # 获取PDF附件的key
        pdf_key = get_pdf_attachment_key(item)
        print(f"pdf_key: {pdf_key}")
        if not pdf_key:
            print(f"条目 {item_key} 没有PDF附件")
            return
            
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 构造输出文件名
        title = item.get('data', {}).get('title', 'untitled')
        # 清理文件名中的非法字符
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}.pdf"
        
        # 下载PDF
        print(f"正在下载: {filename}")
        client.download_file(pdf_key, output_path / filename)
        print(f"下载完成: {output_path / filename}")
        
    except Exception as e:
        print(f"下载过程中发生错误: {str(e)}")

def main():
    client = ZoteroLocal()
    
    # 下载特定条目的PDF
    item_key = "M8GF26XB"  # 条目的key
    download_item_pdf(client, item_key)

if __name__ == "__main__":
    main() 
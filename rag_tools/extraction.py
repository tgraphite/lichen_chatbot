import os
import re
from bs4 import BeautifulSoup


def sanitize_filename(filename):
    # 清理非法文件名字符并限制长度
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)[:120]
    return cleaned.strip(".")


def extract_title_and_content(html_file_path):
    try:
        with open(html_file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # 提取标题（从h1标签或页面标题）
        h1_tag = soup.find("h1", class_="post-title")
        if h1_tag:
            title = h1_tag.get_text().strip()
        else:
            title = soup.title.get_text().split(" - ")[0].strip()

        # 提取正文内容
        content_div = soup.find("div", class_="post-content")
        if not content_div:
            return None, None

        # 移除不需要的元素
        for element in content_div(
            ["script", "style", "div.widget", "ul.widget-list", "h1.post-title"]
        ):
            element.decompose()

        # 获取处理后的文本内容
        content = "\n".join(
            [
                p.get_text().strip()
                for p in content_div.find_all(["p", "li", "h2", "h3"])
                if p.get_text().strip()
            ]
        )

        return title, content

    except Exception as e:
        print(f"解析错误 {html_file_path}: {str(e)}")
        return None, None


def save_content(title, content, output_dir, filename_base):
    try:
        # 保存为Markdown格式
        md_filename = os.path.join(output_dir, f"{filename_base}.md")
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{content}")

    except Exception as e:
        print(f"保存失败 {filename_base}: {str(e)}")


def process_files(pages_dir="pages", output_dir="texts"):
    os.makedirs(output_dir, exist_ok=True)

    html_files = [f for f in os.listdir(pages_dir) if f.endswith(".html")]
    total = len(html_files)

    for idx, filename in enumerate(html_files):
        file_path = os.path.join(pages_dir, filename)
        print(f"正在处理 [{idx+1}/{total}] {filename}...")

        article_id = filename.split("_")[0]
        title, content = extract_title_and_content(file_path)

        if title and content:
            safe_title = sanitize_filename(title)
            filename_base = f"{article_id}_{safe_title}"
            save_content(title, content, output_dir, filename_base)


if __name__ == "__main__":
    process_files()

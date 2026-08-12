#!/usr/bin/env python3
"""
批量上传课程文件到知识库。

用法：
  python3 batch_upload.py <课程目录> <kb_id>

示例：
  python3 batch_upload.py /sandbox/workspace/outputs/ai-agent-course/AI大模型课程 6sqWuPkFZEoCE2e1n1u7dhjLdQxZqJKbIEgyA3A47os=
"""
import subprocess, sys, os, json

def main():
    if len(sys.argv) < 3:
        print("用法: python3 batch_upload.py <课程目录> <kb_id>")
        sys.exit(1)

    base = os.path.abspath(sys.argv[1])
    kb_id = sys.argv[2]
    upload_script = "/sandbox/workspace/skills/ima-knowledge/scripts/upload_file.py"

    if not os.path.isdir(base):
        print(f"目录不存在: {base}")
        sys.exit(1)

    # 尝试读取 folder_ids.json
    fid_path = os.path.join(base, ".folder_ids.json")
    folder_map = {}
    if os.path.exists(fid_path):
        data = json.load(open(fid_path))
        folder_map = {k: v for k, v in data.get("subs", {}).items()}

    # 按模块文件夹上传
    for mod_dir in sorted(os.listdir(base)):
        mod_path = os.path.join(base, mod_dir)
        if not os.path.isdir(mod_path) or mod_dir.startswith("."):
            continue

        fid = folder_map.get(mod_dir, "")
        for fname in sorted(os.listdir(mod_path)):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(mod_path, fname)
            cmd = [sys.executable, upload_script, "--file-path", fpath, "--knowledge-base-id", kb_id]
            if fid:
                cmd += ["--folder-id", fid]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            ok = "✅" if r.returncode == 0 else "❌"
            print(f"{ok} {mod_dir}/{fname}")

if __name__ == "__main__":
    main()
# -*- encoding: utf-8 -*-
'''
@Time    :   2025/02/13 14:02:22
@Author  :   47bwy
@Desc    :   None
'''

import json

import toml

# 读取 Pipfile.lock
with open("Pipfile.lock", "r") as lock_file:
    lock_data = json.load(lock_file)

# 读取 Pipfile
with open("Pipfile", "r") as pipfile:
    pipfile_data = toml.load(pipfile)

# 更新 Pipfile 中的依赖版本
for section in ["default", "develop"]:
    if section in lock_data:
        for package, info in lock_data[section].items():
            version = info.get("version", "")
            if section == "default":
                pipfile_data["packages"][package] = version
            elif section == "develop":
                pipfile_data["dev-packages"][package] = version

# 写回 Pipfile
with open("Pipfile", "w") as pipfile:
    toml.dump(pipfile_data, pipfile)

print("Pipfile 已更新！")
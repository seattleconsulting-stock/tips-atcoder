import requests
import json
import os
from time import sleep
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.by import By
import subprocess
from subprocess import PIPE
import pyperclip


def main():
    submissions = get_submission_data()
    make_submission_folder(submissions)
    insert_answers(submissions)


def get_submission_data():
    """
    AtCoderのAPIを叩いて、自分の提出履歴を取得する
    """
    api_url = api_path
    response = requests.get(api_url)
    jsonData = response.json()
    # TODO: Python以外の言語の提出も取得できるようにする
    jsonData = list(
        filter(lambda x: x["result"] == "AC" and "Python" in x["language"], jsonData))
    submissions = dict()
    # 各問題の最新の提出を取得する
    for data in jsonData:
        if data["problem_id"] in submissions and submissions[data["problem_id"]]["id"] > data["id"]:
            continue
        submissions[data["problem_id"]] = data
    submissions = list(submissions.values())
    return submissions


def make_submission_folder(submissions):
    """
    AtCoderの提出履歴を元に、フォルダを作成する
    """
    for submission in submissions:
        contest_id = submission["contest_id"].upper()
        os.makedirs(user_path + contest_id, exist_ok=True)


def insert_answers(submissions):
    """
    AtCoderの提出履歴を元に、ファイルを作成する
    """

    driver = webdriver.Chrome()
    for submission in submissions:
        contest_id = submission["contest_id"].upper()
        problem_id = submission["problem_id"][-1]
        sub_url = "https://atcoder.jp/contests/" + \
            contest_id + "/submissions/" + str(submission["id"])

        # 提出コードの取得
        driver.get(sub_url)
        copy_btn = driver.find_elements(By.CLASS_NAME, "btn-copy")[1]
        copy_btn.click()
        code = pyperclip.paste()

        # ファイルパスの設定
        # TODO: Python以外の言語のファイルも作成できるようにする
        path = user_path + contest_id + "/" + problem_id + ".py"

        # 既にファイルが存在する場合はスキップ
        with open(path, "w") as f:
            f.write(code)

        # 自動整形
        # TODO: Python以外の言語のソースコードも自動整形できるようにする
        subprocess.run("autopep8 -i " + path, shell=True,
                       stdout=PIPE, stderr=PIPE, text=True)

        # 負荷軽減のために3秒待機
        sleep(3)

    driver.quit()


if __name__ == '__main__':
    print('Atcoderのユーザー名を入力してください')
    user_id = input()
    user_path = "members/" + user_id + "/"
    unix_second = 0
    api_path = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user=" + \
        user_id + "&from_second=" + str(unix_second)
    main()

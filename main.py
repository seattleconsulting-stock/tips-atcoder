import inquirer
import requests
import json
import os
import pyperclip
import time
from time import sleep
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import subprocess
from subprocess import PIPE


def main():
    submissions = get_submission_data()
    if len(submissions) == 0:
        print("提出履歴がありません")
        return
    pro_bar = ' ' * (len(submissions) - 1)
    print('\r[{0}] {1}/{2}'.format(pro_bar, 0, len(submissions)), end='')
    make_submission_folder(submissions)
    insert_answers(submissions)
    print("\n取得が完了しました")


def get_submission_data():
    """
    AtCoderのAPIを叩いて、自分の提出履歴を取得する
    """
    api_url = api_path
    response = requests.get(api_url)
    jsonData = response.json()
    # TODO: Python以外の言語の提出も取得できるようにする
    jsonData = list(filter(lambda x: x["result"] == "AC" and ("Python" in x["language"] or "PyPy3" in x["language"]), jsonData))
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

    options = Options()
    # ブラウザを表示しない
    options.headless = True
    driver = webdriver.Chrome(options=options)
    for i, submission in enumerate(submissions):
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
        format_code(path)

        # 負荷軽減のために3秒待機
        sleep(3)

        # 進捗を表示
        pro_size = len(submissions)
        pro_bar = ('=' * (i + 1)) + (' ' * (pro_size - i - 1))
        print('\r[{0}] {1}/{2}'.format(pro_bar, i + 1, pro_size), end='')
        time.sleep(0.5)

    driver.quit()

    with open(user_path + "unix_second.txt", "w") as f:
        f.write(str(now))


def format_code(path):
    # TODO: Python以外の言語のソースコードも自動整形できるようにする
    subprocess.run("autopep8 -i " + path, shell=True, stdout=PIPE, stderr=PIPE, text=True)


if __name__ == '__main__':
    # ユーザー名の取得
    print('Atcoderのユーザー名を入力してください')
    user_id = input()
    # ディレクトリパスの取得
    user_path = "members/" + user_id + "/"
    # unix_secondの取得
    if os.path.exists(user_path + "unix_second.txt"):
        f = open(user_path + "unix_second.txt", 'r', encoding='UTF-8')
        unix_second = f.read()
    else:
        unix_second = "0"
    # 現在のunix_secondの取得
    now = int(time.time())
    # 提出した言語の選択
    print("取得したい言語を選択してください")
    # TODO: Python以外の言語の提出も取得できるようにする
    questions = [inquirer.List('language', message="言語", choices=['Python3', 'C++'],),]
    answers = inquirer.prompt(questions)
    # APIのパスの設定
    api_path = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user=" + \
        user_id + "&from_second=" + unix_second
    print("取得中...")
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask web application for the OriginalAkinator game.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import sys
import json
from werkzeug.utils import secure_filename

# Add the src directory to the path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from src.akinator import Akinator, AkinatorNode

app = Flask(__name__)
app.secret_key = "akinator_secret_key"  # 本番環境では安全な秘密鍵を使用してください

# AkinatorインスタンスをFlaskアプリのグローバル変数として保持する
akinator = Akinator()


@app.route('/')
def index():
    """トップページを表示する"""
    return render_template('index.html')


@app.route('/game')
def game():
    """ゲームページを表示する"""
    # セッションを初期化
    session['game_started'] = True
    
    # 新しいゲームを開始
    akinator.start_game()
    
    return render_template('game.html', 
                          question=akinator.get_current_question(),
                          is_question=akinator.is_question())


@app.route('/answer', methods=['POST'])
def answer():
    """ユーザーの回答を処理する"""
    if not session.get('game_started'):
        return redirect(url_for('game'))
    
    # POSTリクエストからデータを取得
    data = request.json
    is_yes = data.get('answer') == 'yes'
    
    # 現在の質問が最終推測かどうか
    if not akinator.is_question():
        # これは推測
        return jsonify({
            'is_question': False,
            'content': akinator.get_current_question(),
            'game_over': True
        })
    else:
        # これは質問
        continue_game = akinator.answer(is_yes)
        
        return jsonify({
            'is_question': akinator.is_question() if continue_game else False,
            'content': akinator.get_current_question(),
            'game_over': not continue_game and not akinator.is_question()
        })


@app.route('/learn', methods=['POST'])
def learn():
    """間違った推測から学習する"""
    if not session.get('game_started'):
        return redirect(url_for('game'))
    
    data = request.json
    correct_answer = data.get('correct_answer')
    distinguishing_question = data.get('distinguishing_question')
    answer_for_correct = data.get('answer_for_correct') == 'yes'
    
    akinator.learn(correct_answer, distinguishing_question, answer_for_correct)
    
    return jsonify({'success': True})


@app.route('/restart', methods=['POST'])
def restart():
    """ゲームを再開する"""
    session['game_started'] = True
    akinator.start_game()
    
    return jsonify({
        'is_question': akinator.is_question(),
        'content': akinator.get_current_question()
    })


@app.route('/admin')
def admin():
    """管理ページを表示する"""
    questions = akinator.get_all_questions()
    return render_template('admin.html', questions=questions)


@app.route('/add_character', methods=['POST'])
def add_character():
    """新しいキャラクターを追加する"""
    character_name = request.form.get('character_name')
    
    # フォームから属性と回答を取得
    character_attributes = {}
    for key, value in request.form.items():
        if key.startswith('attr_'):
            question = key[5:]  # attr_prefixを削除
            character_attributes[question] = value == 'yes'
    
    # 新しい質問を追加
    new_question = request.form.get('new_question')
    if new_question and new_question.strip():
        new_answer = request.form.get('new_answer', 'no')
        character_attributes[new_question] = new_answer == 'yes'
    
    # キャラクターを追加
    akinator.add_character(character_name, character_attributes)
    
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)

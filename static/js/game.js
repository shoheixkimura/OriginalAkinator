// Original Akinator Game JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 要素の取得
    const questionContainer = document.getElementById('question-container');
    const guessContainer = document.getElementById('guess-container');
    const learnContainer = document.getElementById('learn-container');
    const resultContainer = document.getElementById('result-container');
    
    const questionText = document.getElementById('question-text');
    const guessText = document.getElementById('guess-text');
    const wrongGuess = document.getElementById('wrong-guess');
    const resultText = document.getElementById('result-text');
    
    const akinatorImage = document.getElementById('akinator-image');
    
    const yesButton = document.getElementById('yes-button');
    const noButton = document.getElementById('no-button');
    const correctButton = document.getElementById('correct-button');
    const wrongButton = document.getElementById('wrong-button');
    const learnYesButton = document.getElementById('learn-yes-button');
    const learnNoButton = document.getElementById('learn-no-button');
    const playAgainButton = document.getElementById('play-again-button');
    
    const correctAnswer = document.getElementById('correct-answer');
    const distinguishingQuestion = document.getElementById('distinguishing-question');
    
    // イベントリスナーの設定
    yesButton.addEventListener('click', () => answerQuestion('yes'));
    noButton.addEventListener('click', () => answerQuestion('no'));
    correctButton.addEventListener('click', handleCorrectGuess);
    wrongButton.addEventListener('click', handleWrongGuess);
    learnYesButton.addEventListener('click', () => submitLearning('yes'));
    learnNoButton.addEventListener('click', () => submitLearning('no'));
    playAgainButton.addEventListener('click', restartGame);
    
    // Akinatorの画像を変更する関数
    function changeAkinatorImage(state) {
        if (!akinatorImage) return;
        
        switch(state) {
            case 'thinking':
                akinatorImage.src = AKINATOR_IMAGES.thinking;
                break;
            case 'happy':
                akinatorImage.src = AKINATOR_IMAGES.happy;
                break;
            case 'surprised':
                akinatorImage.src = AKINATOR_IMAGES.surprised;
                break;
            default:
                akinatorImage.src = AKINATOR_IMAGES.normal;
        }
    }
    
    // 質問に答える
    function answerQuestion(answer) {
        // 考え中の画像に変更
        changeAkinatorImage('thinking');
        fetch('/answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answer: answer }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.is_question) {
                // 次の質問を表示
                questionText.textContent = data.content;
            // 通常の画像に戻す
            changeAkinatorImage('normal');
                // 通常の画像に戻す
                changeAkinatorImage('normal');
            } else {
                // 推測を表示
                showGuess(data.content);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('エラーが発生しました。もう一度お試しください。');
        });
    }
    
    // 推測を表示
    function showGuess(guess) {
        questionContainer.style.display = 'none';
        guessContainer.style.display = 'block';
        guessText.textContent = guess;
        // ドラマチックな画像に変更
        changeAkinatorImage('surprised');
    }
    
    // 正解の場合の処理
    function handleCorrectGuess() {
        guessContainer.style.display = 'none';
        resultContainer.style.display = 'block';
        document.getElementById('result-title').textContent = '正解しました！';
        resultText.textContent = 'やった！正解することができました！';
        // 嬉しい画像に変更
        changeAkinatorImage('happy');
    }
    
    // 不正解の場合の処理
    function handleWrongGuess() {
        guessContainer.style.display = 'none';
        learnContainer.style.display = 'block';
        wrongGuess.textContent = guessText.textContent;
        // 考える画像に変更
        changeAkinatorImage('thinking');
    }
    
    // 学習データを送信
    function submitLearning(answer) {
        const correctAnswerText = correctAnswer.value.trim();
        const distinguishingQuestionText = distinguishingQuestion.value.trim();
        
        if (!correctAnswerText || !distinguishingQuestionText) {
            alert('すべての項目を入力してください。');
            return;
        }
        
        fetch('/learn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                correct_answer: correctAnswerText,
                distinguishing_question: distinguishingQuestionText,
                answer_for_correct: answer
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                learnContainer.style.display = 'none';
                resultContainer.style.display = 'block';
                document.getElementById('result-title').textContent = '学習完了';
                resultText.textContent = '新しい知識を学びました！ありがとうございます。';
                // 嬉しい画像に変更
                changeAkinatorImage('happy');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('エラーが発生しました。もう一度お試しください。');
        });
    }
    
    // ゲームを再開
    function restartGame() {
        fetch('/restart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            // 全ての要素をリセット
            questionContainer.style.display = 'block';
            guessContainer.style.display = 'none';
            learnContainer.style.display = 'none';
            resultContainer.style.display = 'none';
            
            correctAnswer.value = '';
            distinguishingQuestion.value = '';
            
            questionText.textContent = data.content;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('エラーが発生しました。もう一度お試しください。');
        });
    }
});

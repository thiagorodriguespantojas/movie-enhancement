from flask import Flask, request, jsonify
import os
from process_video import process_video  # Importa a função de processamento de vídeo

app = Flask(__name__)

# Rota para receber o vídeo via POST e processá-lo
@app.route('/process_video', methods=['POST'])
def process_video_api():
    # Verifica se um arquivo foi enviado
    if 'video' not in request.files:
        return jsonify({"error": "Nenhum vídeo enviado"}), 400

    video = request.files['video']
    
    # Salva o vídeo de entrada no servidor
    video_path = 'input_video.mp4'
    video.save(video_path)
    
    # Processar o vídeo usando a função que criamos
    output_video_path = 'output_video.mp4'
    process_video(video_path, output_video_path)

    # Retornar uma mensagem de sucesso após o processamento
    return jsonify({"message": "Vídeo processado com sucesso!", "output_video": output_video_path}), 200

# Iniciar o servidor Flask
#if __name__ == "__main__":
    app.run(debug=True)

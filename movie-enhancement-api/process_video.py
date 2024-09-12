import cv2
import numpy as np
import time

# Função para redimensionar os frames e economizar memória
def resize_frame(frame, scale=0.5):
    # Redimensiona o frame para a escala desejada
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    return resized_frame

# Função para ler e processar o vídeo em blocos
def read_and_process_video_in_chunks(video_path, output_path, chunk_size=100, scale=0.5):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Redimensiona o tamanho do vídeo se necessário
    new_width = int(width * scale)
    new_height = int(height * scale)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (new_width, new_height))

    frames = []
    processed_frames_count = 0

    print(f"Lendo e processando o vídeo em blocos de {chunk_size} frames cada...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Redimensiona o frame para economizar memória
        resized_frame = resize_frame(frame, scale=scale)
        frames.append(resized_frame)
        processed_frames_count += 1

        # Processa o bloco quando atingir o tamanho do chunk ou se todos os frames forem processados
        if len(frames) >= chunk_size or processed_frames_count == total_frames:
            print(f"Processando bloco de {len(frames)} frames...")

            # Estabiliza e ajusta brilho/contraste do bloco
            stabilized_frames = stabilize_video(frames)
            corrected_frames = apply_brightness_contrast_correction(stabilized_frames)

            # Escreve os frames processados no arquivo de saída
            for processed_frame in corrected_frames:
                out.write(processed_frame)
            
            # Limpa os frames já processados para liberar memória
            frames.clear()

    cap.release()
    out.release()
    print("Processamento completo. Vídeo salvo em:", output_path)

# Função para estabilizar o vídeo frame a frame
def stabilize_video(frames):
    stabilized_frames = []
    previous_gray = None
    print("Estabilizando o vídeo...")
    for i, frame in enumerate(frames):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if previous_gray is None:
            previous_gray = gray
            stabilized_frames.append(frame)
            continue

        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(previous_gray, None)
        kp2, des2 = orb.detectAndCompute(gray, None)

        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(des1, des2)

        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        transform, _ = cv2.estimateAffinePartial2D(pts1, pts2)

        stabilized_frame = cv2.warpAffine(frame, transform, (frame.shape[1], frame.shape[0]))

        stabilized_frames.append(stabilized_frame)
        previous_gray = gray

    print(f"Estabilização completa. Total de frames estabilizados: {len(stabilized_frames)}")
    return stabilized_frames

# Função para ajustar brilho e contraste dos frames
def adjust_brightness_contrast(frame, brightness=0, contrast=30):
    return cv2.convertScaleAbs(frame, alpha=1 + contrast / 127.0, beta=brightness)

# Função para aplicar a correção de brilho e contraste
def apply_brightness_contrast_correction(frames):
    corrected_frames = []
    print("Ajustando brilho e contraste...")
    for frame in frames:
        corrected_frame = adjust_brightness_contrast(frame)
        corrected_frames.append(corrected_frame)
    print(f"Correção de brilho e contraste aplicada. Total de frames corrigidos: {len(corrected_frames)}")
    return corrected_frames

# Função principal para processar o vídeo
def process_video(input_video_path, output_video_path, chunk_size=100, scale=0.5):
    print(f"Processando o vídeo: {input_video_path}")
    start_time = time.time()  # Marca o início do processamento
    read_and_process_video_in_chunks(input_video_path, output_video_path, chunk_size, scale)
    end_time = time.time()  # Marca o término do processamento
    elapsed_time = end_time - start_time
    print(f"Tempo total de processamento: {elapsed_time:.2f} segundos")

# Exemplo de uso
if __name__ == "__main__":
    process_video('timelapse_input.mp4.mp4', 'timelapse_output.mp4', chunk_size=100, scale=0.5)

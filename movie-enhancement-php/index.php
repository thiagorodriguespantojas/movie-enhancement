<?php
// Verifica se o vídeo foi enviado
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['video'])) {
    // Diretório de upload
    $upload_dir = 'upload/';
    $output_dir = 'output/';
    
    // Certifique-se de que os diretórios existem
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir, 0777, true);
    }
    if (!is_dir($output_dir)) {
        mkdir($output_dir, 0777, true);
    }

    // Nome do arquivo de upload
    $video_name = basename($_FILES['video']['name']);
    $upload_path = $upload_dir . $video_name;
    
    // Move o vídeo para o diretório de upload
    if (move_uploaded_file($_FILES['video']['tmp_name'], $upload_path)) {
        // Caminho de saída para o vídeo processado
        $output_path = $output_dir . 'processed_' . $video_name;
        
        // Marca o tempo de início
        $start_time = microtime(true);

        // Comando FFmpeg para processar o vídeo (ajustando brilho, por exemplo)
        $command = "ffmpeg -i $upload_path -vf 'eq=brightness=0.05' $output_path";
        
        // Executa o comando FFmpeg
        shell_exec($command);
        
        // Marca o tempo de fim
        $end_time = microtime(true);
        
        // Calcula o tempo de processamento
        $processing_time = round($end_time - $start_time, 2);

        // Retorna o caminho do vídeo processado e o tempo de processamento
        echo json_encode([
            'status' => 'success',
            'message' => 'Vídeo processado com sucesso!',
            'output_video' => $output_path,
            'processing_time' => $processing_time . ' segundos'
        ]);
    } else {
        echo json_encode([
            'status' => 'error',
            'message' => 'Erro ao fazer upload do vídeo'
        ]);
    }
} else {
    echo json_encode([
        'status' => 'error',
        'message' => 'Nenhum vídeo enviado'
    ]);
}
?>

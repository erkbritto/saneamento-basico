#!/usr/bin/env python3
import cv2
import numpy as np

def debug_histogram_shapes():
    """Debug para verificar o comportamento dos histogramas OpenCV"""
    print('=== DEBUG DE HISTOGRAM SHAPES ===')
    
    # Cria uma imagem de teste simples
    test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(test_image, cv2.COLOR_BGR2HSV)
    
    print(f'Gray shape: {gray.shape}')
    print(f'HSV shape: {hsv.shape}')
    
    # Testa diferentes configurações de histograma
    
    # Configuração 1: Como em extract_face_encoding
    print('\n--- Configuração 1 (extract_face_encoding) ---')
    hist1 = cv2.calcHist([gray], [0], None, [101], [0, 256])
    print(f'hist_gray shape: {hist1.shape}')
    print(f'hist_gray flatten shape: {hist1.flatten().shape}')
    
    hist2 = cv2.calcHist([hsv], [0], None, [1], [0, 180])
    print(f'hist_h shape: {hist2.shape}')
    print(f'hist_h flatten shape: {hist2.flatten().shape}')
    
    hist3 = cv2.calcHist([hsv], [1], None, [1], [0, 256])
    print(f'hist_s shape: {hist3.shape}')
    print(f'hist_s flatten shape: {hist3.flatten().shape}')
    
    # Normaliza
    hist1_norm = cv2.normalize(hist1, hist1).flatten()
    hist2_norm = cv2.normalize(hist2, hist2).flatten()
    hist3_norm = cv2.normalize(hist3, hist3).flatten()
    
    print(f'hist1_norm shape: {hist1_norm.shape}')
    print(f'hist2_norm shape: {hist2_norm.shape}')
    print(f'hist3_norm shape: {hist3_norm.shape}')
    
    # Concatena
    features1 = np.concatenate([
        hist1_norm,
        hist2_norm,
        hist3_norm,
        [gray.mean(), gray.std()]
    ])
    print(f'Features1 shape: {features1.shape}')
    
    # Configuração 2: Teste com flatten direto
    print('\n--- Configuração 2 (flatten direto) ---')
    hist1_flat = cv2.calcHist([gray], [0], None, [101], [0, 256]).flatten()
    hist2_flat = cv2.calcHist([hsv], [0], None, [1], [0, 180]).flatten()
    hist3_flat = cv2.calcHist([hsv], [1], None, [1], [0, 256]).flatten()
    
    print(f'hist1_flat shape: {hist1_flat.shape}')
    print(f'hist2_flat shape: {hist2_flat.shape}')
    print(f'hist3_flat shape: {hist3_flat.shape}')
    
    features2 = np.concatenate([
        hist1_flat,
        hist2_flat,
        hist3_flat,
        [gray.mean(), gray.std()]
    ])
    print(f'Features2 shape: {features2.shape}')
    
    # Configuração 3: Verifica se há diferença
    print('\n--- Comparação ---')
    print(f'Features1 == Features2: {np.array_equal(features1, features2)}')
    print(f'Diferença máxima: {np.max(np.abs(features1 - features2))}')
    
    # Verifica componentes individuais
    print('\n--- Análise dos componentes ---')
    print(f'101 bins (gray): {len(hist1_norm)}')
    print(f'1 bin (H): {len(hist2_norm)}')
    print(f'1 bin (S): {len(hist3_norm)}')
    print(f'mean + std: 2')
    print(f'Total esperado: {101 + 1 + 1 + 2}')
    print(f'Total real: {len(features1)}')

if __name__ == '__main__':
    debug_histogram_shapes()

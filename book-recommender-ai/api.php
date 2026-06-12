<?php

    // Precisa de 3 coisas:
    // userInput
    // systemPrompt
    // response

    header('Content-Type: application/json');
    header('Access-Control-Allow-Origin: *');

    $API_Key = 'AIzaSyDI3wgUW9czX5Vixi6vGsLmIEnB4Yfh1-c';

    // Pega o que o JS enviou via fetch
    $input = json_decode(file_get_contents('php://input'), true);

    if( isset($input['message']) )
    {
        $userInput = $input['message'];
    }
    else
    {
        http_response_code(400);
        echo json_encode( ['error' => 'Empty message'] );
        exit;
    }

    $systemPrompt = "
    Você é um especialista em literatura e um assistente dedicado à recomendação de livros.

    Seu objetivo é recomendar obras literárias relevantes com base no humor, emoções, temas, autores ou preferências descritas pelo usuário.
    
    Regras:
    
    - Se o usuário estiver explorando ideias ou conversando sobre literatura, converse brevemente e faça perguntas quando necessário antes de recomendar.
    Quando fizer recomendações, indique exatamente 3 livros.
    - Para cada livro informe:
      • Título
      • Autor
      • Uma explicação curta e clara de por que a obra combina com o pedido do usuário.
    - Priorize literatura, clássicos, ficção literária e obras com valor artístico ou intelectual.
    - Evite livros de autoajuda ou recomendações genéricas, a menos que o usuário peça explicitamente.
    - Não invente livros ou autores.
    - Mantenha as respostas concisas e organizadas.
    - Nunca mude de assunto ou responda temas que não sejam relacionados a livros e literatura.
    - Sempre responda no mesmo idioma usado pelo usuário.
    
    O tom deve ser refinado, acolhedor e apaixonado por literatura.
    ";

    $body = json_encode([
        'system_instruction' =>
        [ 
            'parts' =>
            [
                [
                    'text' => $systemPrompt
                ]
            ]
        ],
        'contents' =>
        [
            [
                'parts' =>
                [
                    [
                        'text' => $userInput
                    ]
                ]
            ]
        ]
    ]);

    // Testando o envio do JSON para a API
    //print('<pre>');print_r($body);exit;

    $ch = curl_init("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'x-goog-api-key:'. $API_Key
    ]);

    $response = curl_exec($ch);
    $curlTime = curl_getinfo($ch, CURLINFO_TOTAL_TIME);
    curl_close($ch);

    $data = json_decode($response, true);

    // Testando a resposta (Array) da API
    //print_r($data);exit;

    // Tratando erros vindos da API
    if(isset($data['error']))
    {
        $reply = 'Gemini API error: '.$data['error']['message'];
    }

    // Esse aninhamento é como Gemini retorna
    if( isset($data['candidates'][0]['content']['parts'][0]['text']) )
        $reply = $data['candidates'][0]['content']['parts'][0]['text'];
    else
    {
        $reply = 'No response.';
    }

    // Enviando a resposta em JSON para o JS
    echo json_encode([ 
        'reply' => $reply,
        'response_time' => round($curlTime,2),
        'modelVersion' => ucfirst($data['modelVersion']),
        'promptTokenCount' => $data['usageMetadata']['promptTokenCount'],
        'candidatesTokenCount' => $data['usageMetadata']['candidatesTokenCount'],
        'thoughtsTokenCount' => $data['usageMetadata']['thoughtsTokenCount'],
        'totalTokenCount' => $data['usageMetadata']['totalTokenCount']
    ]);
?>
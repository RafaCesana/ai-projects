
const btn       = document.getElementById('btn');
const input     = document.getElementById('userInput');
const chatBox   = document.getElementById('chatBox');


function addMessage(text, type)
{
    // Adding message to ChatBox (User and AI conversation)
    const div = document.createElement('div');
    div.classList.add('p-3','rounded-3');

    if(type === 'user')
    {
        div.classList.add('bg-primary','text-white','align-self-end','ms-5');
    }
    else
    {
        if(type === 'ai')
        {
            div.classList.add('border','border-secondary','text-light','me-5');
            div.style.background = 'rgba(255,255,255,0.05);'
        }
        else
        {
            div.classList.add('text-secondary','fst-italic');
        }
    }

    div.style.whiteSpace = 'pre-wrap';
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}


btn.addEventListener('click', async () => {
    const userInput = input.value.trim();

    if(!userInput)
        return;

    addMessage(userInput, 'user');

    // Desabilitando o botão pra aguardar a resposta da ia.
    input.value = '';
    btn.disabled = true;

    const loading = addMessage('Thinking...', 'loading');

    // Enviando a requisicao http pro php
    try
    {
        const response = await fetch('api.php', {
            method:'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput })
        });

        const data = await response.json();
        
        loading.remove();
        addMessage(`${data.reply}\n\nGenerated in ${data.response_time}s · ${data.modelVersion} · ${data.totalTokenCount} tokens\ninput: ${data.promptTokenCount} · output: ${data.candidatesTokenCount} · thinking: ${data.thoughtsTokenCount}`,'ai');
    }
    catch (error)
    {
        loading.remove();
        addMessage('Erro ao conectar com a IA.','ai');
        console.log(error);
    }

    btn.disabled = false;

});
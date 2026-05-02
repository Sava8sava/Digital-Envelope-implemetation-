# Digital-Envelope-implemetation-

# 1.Source code 

## Inteface
1.1 Input do usuario para criação do envelope: Mensagem, o nome do arquivo de saida da mensagem, sua chave privada usada para assinatura e a chave publica do destinatario(o string path do arquivo delas)
- caso o usario não tenha o par de chaves assimetricas, existe uma função no arquivo assimetrickeys.py que geram um par(mas lembrando a entrada é chave privada do remetente e a **publica do destinatario**)  
2. A chave de sessão é gerada pelo proprio envelope(ela acaba sendo mostrada no terminal pq eu tive que testar no cyberchef - Felipe) 
3. a mensagem vai ser envelopada e tera a seguinte saida: um arquivo mensagem cifrado, a chave de sessão cifrada, e a assinatura(eu não identifiquei se o aplicativo deve fazer o envio, ou se o envio do arquivo pode ser feito por qualquer meio como email ou zapzap, perguntar pro candre depois) 
4. Em caso de algum erro no processo de criação do envelope a inteface não pode deixar de funcionar, ela deve informar ao usario qual foi o erro(na criação do envelope cada etapa retorna uma variavel booleana como status, e um segunda saida que pode ser o resultado da função ou uma mensagem de sucesso em caso de true, ou False acompanhada de uma mensagem que identifica o erro 

1.2 Input do usuario para abrir o envelope: Os três arquivos que formam o envelope, a chave privada do usuario, a chave publica do remetente para checar a assinatura 
1. O aplicativo ira mostrar(ou criar um arquivo) da mensagem decifrada e um identificação que a mensagem é valida via assinatura digital 
2. ainda não identifiquei se o aplicativo deve mostrar tambem a chave de sessão em hex
3. assim como o anterior todas as funções dessa classe retornam o status booleano + mensagem de status ou resultado 

## Alguns detalhes pertinentes 
- O envelope para um primeiro teste foi extremamente hard coded, ele ainda não esta preparado para receber as entradas da interface diretamente, mas durante a criaçõ da interface eu pretendo resolver
- Os arquivos de chave assimetrica estão em .pem como exigido trabalho
- como eu não testei com outro grupo o formato dos arquivos de saida não esta padronizado  

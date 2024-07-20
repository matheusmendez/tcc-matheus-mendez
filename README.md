# tcc
 
Trabalho de conclusão de curso: Desenvolvimento de um sistema de monitoramento de temperatura e umidade para fábrica de eletrônicos do polo industrial de Manaus.
---
## Dispositivo de Medição
### Requisitos:
- 01 - ESP32 Devkit V1
- 01 - DHT22
- 01 - Display LCD 16x2 I2C
- 01 - Buzzer Contínuo Ativo 3V-24V
- 02 - Resistor 120Ω
- 01 - Relé 5V
- 01 - Fonte DC 12V plug P4
- 01 - Plug P4 Fêmea
- 01 - Plug P4 Macho
- 01 - Conjunto de jumpers para conexão
### Montagem:
A montagem do circruito pode ser realizada de acordo com a simulação disponível no link:
[Simulação - Wokwi](https://wokwi.com/projects/403956833013289985)
### Firmware
1. Para utilização do firmware desenvolvido é necessário instalar o micropython no ESP32. O tutorial oficial para instalação se encontra no site oficial do Micropython: [Tutorial](https://docs.micropython.org/en/latest/esp32/tutorial/index.html).
2. Após a intalação, copie os arquivos da pasta Dispositivo/firmware para o ESP32.
3. Ajuste o valor das variáveis do arquivo "config.json" de acordo com as suas credenciais de rede.
### Caixa (Opcional):
Os modelos 3D das partes da caixa estão disponilizados nos links:
- [Caixa Montada](https://cad.onshape.com/documents/5ee563dabc5cf40dcc17a705/w/58cd88480544ae4f2f2674a2/e/ea1d19a6e14d2dda4d9e5ee0?renderMode=0&uiState=669c1ebdb32bef24137163c0)
- [Tampa](https://cad.onshape.com/documents/3d8aa507a34cd4c12f23734a/w/b65159fd5eff1da20cd30483/e/95e7f77ebec7b55297b8c4c9?renderMode=0&uiState=669c1f063b57660b633c96ce)
- [Caixa](https://cad.onshape.com/documents/34db8131c61f739183f87539/w/d9c9ee5d3cfbf7ce4d2ebe6c/e/afad426d46ba18abfd25e274?renderMode=0&uiState=669c1f363b57660b633c973d)

---
## Web-Server
### Requisitos:
- Git: [Tutorial de instalação](https://github.com/git-guides/install-git)
- Docker-Compose: [Tutorial de instalação](https://docs.docker.com/compose/install/)
### Instalação
1. Baixe esse repositório com o comando de terminal:
```terminal
git clone https://github.com/matheusmendez/tcc-matheus-mendez.git
```
2. Crie uma varial chamada ".env" na pasta raiz do projeto e configure as variáveis de acordo com o exemplo ".env_exemplo".
3. Abra o terminal de comandos na pasta principal do projeto e crie os containers Docker com o seguinte comando:
```terminal
docker compose up.d
```
4. Abra um navegador e insira o ip do seu computador ou "localhost" na barra de endereços.
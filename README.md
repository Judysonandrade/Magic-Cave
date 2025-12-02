# Magic Cave

**Magic Cave** é um jogo de ação e plataforma 2D desenvolvido em Python utilizando a biblioteca **Pygame Zero**. O jogador controla um herói que deve navegar por cavernas perigosas, pular poços de lava e derrotar Ogros para destrancar a porta de saída.

## Funcionalidades do Jogo

* **3 Níveis de Dificuldade:** Dificuldade progressiva com mais inimigos e posicionamentos complexos.
* **IA Inteligente de Inimigos:** Os inimigos patrulham a área e **pulam buracos automaticamente** para perseguir o jogador.
* **Sistema de Combate:** Mecânica de ataque corpo-a-corpo com tempo de recarga (cooldown) e hitboxes.
* **Lógica de Progressão:** A porta de saída permanece trancada até que **TODOS os inimigos** da fase sejam derrotados.
* **Sistema de Áudio:** Música de fundo para menus e efeitos sonoros para passos, ataques e vitória.
* **Estados de Jogo:** Telas totalmente funcionais de Menu, Instruções, Jogo, Game Over e Vitória.

## Controles

| Tecla | Ação |
| :--- | :--- |
| **Setas** | Mover Esquerda / Direita |
| **Espaço** | Pular |
| **X** | Atacar |
| **A** | Pular Fase (Cheat/Debug) |
| **O** | Ligar/Desligar Som (Mute) |

## Tecnologias Utilizadas

* **Python 3**
* **Pygame Zero (pgzero)**
* **Pygame** (Utilizado apenas para manipulação de colisão com `Rect`)

## Como Rodar o Jogo

1.  **Pré-requisitos:** Certifique-se de ter o Python instalado.
2.  **Instalar Pygame Zero:**
    ```bash
    pip install pgzero
    ```
3.  **Executar o jogo:**
    ```bash
    python game.py
    ```

## Estrutura do Projeto

* `game.py`: Loop principal do jogo e lógica.
* `images/`: Sprites para o herói, inimigos e blocos do cenário.
* `sounds/`: Efeitos sonoros curtos (formato WAV).
* `music/`: Faixas de música de fundo.

---
*Desenvolvido para fins educacionais, demonstrando conceitos de Orientação a Objetos (OOP), Física e Loop de Jogo.*

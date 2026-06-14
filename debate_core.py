# -*- coding: utf-8 -*-
import pygame
import os
import sys
import random
import textwrap
import pyperclip
from datetime import datetime
from openai import OpenAI

# ATUALIZAÇÃO: Dicionários de prompts e pautas permanecem centrais
# (Estes são os mesmos da versão anterior, pois você não pediu para alterá-los)
PROMPTS_COMPLETOS = {
    "luciana": {
        "persona": "Você é uma professora de direita moderada, classe média, com boa didática. Inspirada no estilo intelectual de Roger Scruton, você é uma acadêmica erudita, elegante e defensora da tradição, da liberdade responsável e do conservadorismo cultural. Seu objetivo é apresentar aos alunos uma perspectiva equilibrada, enfatizando a liberdade individual, a meritocracia e a importância de instituições sólidas. Utilize autores que apoiem o liberalismo clássico e o conservadorismo moderno, argumentando com lógica, clareza e exemplos concretos. Mantenha um tom acessível, sem ser simplista. Seja cordial, mas firme em suas posições. Limite suas respostas a 100 palavras e nunca use seu nome.",
        "iniciativa": 5
    },
    "luigi": {
        "persona": "Você é um professor de esquerda moderada, classe média, com boa didática. Seu objetivo é fazer os alunos entenderem o tema de forma aprofundada, com explicações claras e bem estruturadas. Cite autores e correntes teóricas relevantes. Desenvolva argumentos com progressão lógica e objetividade, sem soar robótico. Seja cortês, mas reafirme sua visão como correta. Baseie-se no estilo de Leandro Karnal, sem mencioná-lo. Não utilize seu nome. Limite suas respostas a 100 palavras.",
        "iniciativa": 5
    },
    "sofia": {
        "persona": "Você é uma adolescente de classe média alta com uma vibe de 'coach' — sempre motivada, cheia de frases prontas e lições de vida. Fala como se estivesse dando um TED Talk: 'Acorda pra vida, pivete!' e 'Se não tem meta, vira estatística!'. Use exemplos do dia a dia, como 'Meu primo virou influencer em 6 meses só postando todo dia'. Você acha que qualquer problema se resolve com 'foco' e 'atitude'. Interaja tentando transformar tudo em lição motivacional. Respostas curtas (até 45 palavras), diretas e sem pessimismo. Nunca use seu nome.",
        "iniciativa": 4
    },
    "juliana": {
        "persona": "Você é uma adolescente que vive no modo 'concorda com tudo'. Evita conflitos a todo custo, concordando com qualquer opinião para não arrumar confusão. Muda de ideia rapidamente se alguém contesta, mantendo-se sempre neutra. Suas respostas são evasivas, curtas (até 45 palavras) e repletas de frases que demonstram indecisão, como justificativas genéricas ou tentativas de agradar a todos sem se comprometer. Nunca use seu nome.",
        "iniciativa": 1
    },
    "mateus": {
        "persona": "Você é um adolescente religioso de classe média, tranquilo, mas convicto em sua fé. Valoriza a caridade, a família e a ética, mas evita julgamentos. Quando fala de temas polêmicos, usa exemplos práticos alinhados com seus pensamentos. Reconhece falhas da igreja, mas acredita no amor ao próximo. Fala de maneira simples, sem citar versículos diretos. Respostas de até 80 palavras e sem citar seu nome.",
        "iniciativa": 3
    },
    "vinicius": {
        "persona": "Você é um adolescente de classe média baixa que já viu de tudo e não se ilude mais. Não é revoltado, apenas encarou a realidade cedo. Trabalha meio período e sabe que o sistema é injusto, mas segue em frente. Fala com um misto de cansaço e ironia: 'Boa sorte tentando mudar isso aí'. Não cai em papo de político nem de coach. Reconhece seus privilégios: 'Pelo menos tenho teto'. Interage com respostas secas e pé no chão. Limite suas respostas a 45 palavras e nunca use seu nome.",
        "iniciativa": 2
    },
    "mariana": {
        "persona": "Você é uma adolescente conservadora de classe alta, com um jeito imaturo e 'debatedor'. Use gírias sem exagero. Seu foco é entender como os temas afetam sua vida e a sociedade. Cite ideias conservadoras quando relevante. Baseie-se em Jade Picon, sem mencioná-la. Sua inteligência equivale a uma aluna nota 8. Responda com até 45 palavras e não use seu nome.",
        "iniciativa": 4
    },
    "lucas": {
        "persona": "Você é um estudante progressista de classe média, curioso e reflexivo. Preocupa-se com desigualdade, privilégios e direitos sociais. Questiona contextos históricos e seus impactos atuais. Sua fala é informal, sem termos técnicos ou repetições. Prefira destacar convergências antes de discordar, mas seja firme contra injustiças. Use exemplos cotidianos, sem citar autores. Baseie-se em Lázaro Ramos jovem, sem mencioná-lo. Sua inteligência equivale a um aluno nota 9. Responda com até 80 palavras e não use seu nome.",
        "iniciativa": 3
    },
    "carlos": {
        "persona": "Você é um jovem de classe baixa, pragmático e irônico. Prefere exemplos do dia a dia em vez de teorias. Ilustre dificuldades ligadas à pobreza com histórias do seu bairro ou da sua família. Às vezes, usa sarcasmo. Você é negro e ocasionalmente sente preconceito. Baseie-se em MC Poze do Rodo, sem mencioná-lo. Sua inteligência equivale a um aluno nota 7. Responda com até 45 palavras e não use seu nome.",
        "iniciativa": 4
    }
}
PAUTAS_DEBATE = {
    "Deportação de Imigrantes Ilegais": "A questão da deportação de imigrantes ilegais é um tema que divide opiniões em todo o mundo. De um lado, há o argumento de que a imigração irregular sobrecarrega serviços públicos, pressiona o mercado de trabalho e pode representar um risco à segurança nacional. Por outro lado, a maioria dos imigrantes ilegais foge de situações extremas, como conflitos ou crises econômicas. Além disso, essas pessoas frequentemente ocupam funções essenciais na economia. O debate de hoje explorará se a deportação em massa é uma solução eficaz ou se políticas de regularização seriam mais humanas e benéficas.",
    "Voto Obrigatório Vs. Voto Facultativo": "O voto obrigatório é defendido como forma de garantir maior representatividade, evitando que apenas grupos engajados determinem os rumos do país. Críticos, porém, argumentam que obrigar alguém a votar viola a liberdade individual e que um eleitor desinteressado pode comprometer a qualidade da democracia, enquanto o voto facultativo respeita a escolha, mas pode reduzir a participação e favorecer elites. Qual modelo é mais adequado para fortalecer a democracia?",
    "Cotas Raciais e Sociais na Educação": "As políticas de cotas surgiram como resposta às desigualdades estruturais no Brasil, visando promover o acesso de grupos marginalizados às universidades. Estudos indicam que cotistas têm desempenho similar aos não cotistas, desmistificando a ideia de que as cotas reduzem a qualidade do ensino. Críticos, no entanto, argumentam que o sistema reforça divisões raciais e não ataca a raiz do problema: a precariedade da educação básica. As cotas são uma ferramenta eficaz ou há alternativas mais justas?",
    "Impacto do Desenvolvimento Tecnológico": "A inovação tecnológica aumenta a produtividade e o lucro, sendo essencial para a sobrevivência no capitalismo. No entanto, ela não é neutra e reflete os interesses das classes dominantes, transformando as relações de trabalho e podendo ampliar a desigualdade. Por outro lado, a tecnologia também cria oportunidades para resistências e novas formas de organização. Vamos discutir como essas transformações moldam os sistemas produtivos e os impactos sociais da relação entre tecnologia, capital e trabalho."
}


class AssetManager:
    def __init__(self):
        self.base_path = "assets"
        self._cache = {}

    def load_image(self, filename, alpha=False):
        if filename in self._cache:
            return self._cache[filename]
        try:
            path = os.path.join(self.base_path, filename)
            img = pygame.image.load(path)
            img = img.convert_alpha() if alpha else img.convert()
            self._cache[filename] = img
            return img
        except pygame.error:
            print(f"ERRO: Imagem '{filename}' não encontrada em '{self.base_path}'.")
            fallback = pygame.Surface((100, 100), pygame.SRCALPHA if alpha else 0)
            fallback.fill((255, 0, 0))
            return fallback


class Renderer:
    def __init__(self, screen, font, big_font):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.text_box_height = 180
        self.text_box_y = self.height - self.text_box_height - 10
        self.font = font
        self.big_font = big_font

    def draw_background(self, image):
        try:
            img_w, img_h = image.get_size()
            scale = max(self.width / img_w, self.height / img_h)
            scaled = pygame.transform.smoothscale(image, (int(img_w * scale), int(img_h * scale)))
            self.screen.blit(scaled, (0, 0), (
                (scaled.get_width() - self.width) // 2, (scaled.get_height() - self.height) // 2, self.width,
                self.height))
        except:
            self.screen.fill((100, 100, 100))

    def draw_character(self, image, position, darken=False, size=(300, 400)):
        if darken:
            image = image.copy()
            image.fill((70, 70, 70, 0), special_flags=pygame.BLEND_RGBA_SUB)

        scaled = pygame.transform.scale(image, size)
        x_pos = 70 if position == "left" else self.width - size[0] - 70
        y_pos = self.text_box_y - size[1] + 40
        self.screen.blit(scaled, (x_pos, y_pos))

    def draw_text_box(self, name, text_lines, has_more_text=False):
        box_rect = pygame.Rect(100, self.text_box_y, self.width - 200, self.text_box_height)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 0, 0), box_rect, 3, border_radius=12)

        name_surface = self.big_font.render(name, True, (0, 0, 0))
        name_bg = pygame.Surface((name_surface.get_width() + 20, name_surface.get_height() + 8))
        name_bg.fill((230, 230, 230))
        name_bg.blit(name_surface, (10, 4))
        self.screen.blit(name_bg, (110, self.text_box_y + 8))

        for i, line in enumerate(text_lines):
            text_surface = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text_surface, (130, self.text_box_y + 60 + i * 28))

        # ATUALIZAÇÃO: Posição do botão "Continuar" ajustada para dentro da caixa
        if has_more_text:
            btn_rect = pygame.Rect(box_rect.right - 160, box_rect.bottom - 50, 150, 40)
            pygame.draw.rect(self.screen, (220, 220, 220), btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, (0, 0, 0), btn_rect, 2, border_radius=8)
            text = self.font.render("Continuar", True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=btn_rect.center))

    def draw_end_message(self):
        box_rect = pygame.Rect(100, self.text_box_y, self.width - 200, self.text_box_height)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 0, 0), box_rect, 3, border_radius=12)
        end_text = self.big_font.render("Fim do Debate", True, (0, 0, 0))
        self.screen.blit(end_text, end_text.get_rect(center=(box_rect.centerx, box_rect.centery - 20)))
        return self.draw_close_button()

    def draw_close_button(self):
        btn_rect = pygame.Rect(self.width // 2 - 75, self.text_box_y + self.text_box_height - 70, 150, 50)
        pygame.draw.rect(self.screen, (0, 123, 255), btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), btn_rect, 2, border_radius=10)
        text = self.font.render("Fechar", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=btn_rect.center))
        return btn_rect

    def save_screenshot(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pygame.image.save(self.screen, filename)
        print(f"Screenshot salvo como {filename}")


class DialogueSystem:
    def __init__(self, font, max_width):
        self.font = font
        self.max_width = max_width - 60  # Largura útil da caixa com margens
        self.current_page, self.pages, self.current_char, self.last_update = 0, [], 0, 0
        self.typing_speed, self.max_lines = 30, 3  # Reduzido para evitar sobreposição com o botão

    def smart_wrap(self, text):
        # ATUALIZAÇÃO: Lógica de quebra de linha ajustada para caber na caixa de diálogo
        avg_char_width = self.font.size("a")[0]
        wrap_limit = self.max_width // avg_char_width if avg_char_width > 0 else 80

        wrapped_text = textwrap.wrap(text, width=wrap_limit, replace_whitespace=False, drop_whitespace=True)
        self.pages = [wrapped_text[i:i + self.max_lines] for i in range(0, len(wrapped_text), self.max_lines)]
        if not self.pages:  # Garante que haja ao menos uma página vazia se o texto for vazio
            self.pages = [[]]
        self.current_page, self.current_char = 0, 0
        self.last_update = pygame.time.get_ticks()

    def update_typing(self):
        if pygame.time.get_ticks() - self.last_update > self.typing_speed:
            self.last_update = pygame.time.get_ticks()
            self.current_char += 1
            return True
        return False

    def get_current_text(self):
        if self.current_page >= len(self.pages): return []
        current_lines, typed_lines, rem_chars = self.pages[self.current_page], [], self.current_char
        total_chars_in_lines = 0
        for line in current_lines:
            line_len = len(line)
            if self.current_char > total_chars_in_lines + line_len:
                typed_lines.append(line)
                total_chars_in_lines += line_len
            else:
                chars_to_show = self.current_char - total_chars_in_lines
                typed_lines.append(line[:chars_to_show])
                break
        return typed_lines

    def is_page_complete(self):
        if self.current_page >= len(self.pages): return True
        return self.current_char >= sum(len(line) for line in self.pages[self.current_page])

    def has_more_pages(self):
        return self.current_page < len(self.pages) - 1

    def next_page(self):
        if self.has_more_pages(): self.current_page, self.current_char = self.current_page + 1, 0; return True
        return False

    def complete_current_page(self):
        if self.current_page < len(self.pages): self.current_char = sum(
            len(line) for line in self.pages[self.current_page])


class DebateSimulator:
    def __init__(self, chave_api, nomes_personagens, ordem_falantes, pauta_texto):
        chave_api = (chave_api or "").strip()
        if not chave_api:
            raise ValueError("A chave da API da OpenAI não foi fornecida.")
        self.client = OpenAI(api_key=chave_api)
        self.MODEL_NAME = "gpt-4o-mini"
        self.ORDEM_FALANTES = ordem_falantes
        self.MAX_HISTORICO = 6
        self.personas = {nome: PROMPTS_COMPLETOS.get(nome) for nome in nomes_personagens}
        self.historico = [{"falante": self.ORDEM_FALANTES[0], "texto": pauta_texto}]
        self.ultimo_falante = self.ORDEM_FALANTES[0]
        self.turnos_por_falante = {nome: 0 for nome in self.ORDEM_FALANTES}
        self.turnos_por_falante[self.ultimo_falante] = 1
        self.next_turn = None

    def gerar_resposta(self, mensagens):
        try:
            response = self.client.chat.completions.create(model=self.MODEL_NAME, messages=mensagens, temperature=0.7)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro na API OpenAI: {e}")
            return "Ocorreu um erro ao conectar com a IA. Verifique sua chave e conexão."

    def escolher_proximo_falante(self):
        candidatos = [nome for nome in self.ORDEM_FALANTES if nome != self.ultimo_falante]
        if not candidatos:
            return self.ultimo_falante

        maior_numero_de_turnos = max(self.turnos_por_falante.values())
        pesos = []
        for nome in candidatos:
            iniciativa = self.personas.get(nome, {}).get("iniciativa", 1)
            bonus_participacao = maior_numero_de_turnos - self.turnos_por_falante.get(nome, 0) + 1
            pesos.append(max(1, iniciativa) * bonus_participacao)

        return random.choices(candidatos, weights=pesos, k=1)[0]

    def get_proximo_falante(self):
        return self.escolher_proximo_falante()

    def proximo_turno(self, pregenerate_next=False):
        proximo = self.escolher_proximo_falante()
        contexto = [f"{f['falante'].upper()}: {f['texto']}" for f in self.historico[-self.MAX_HISTORICO:]]

        mensagens_para_ia = [
            {"role": "system", "content": self.personas[proximo]['persona']},
            {"role": "user", "content": "CONTEXTO DO DEBATE:\n" + "\n".join(contexto)}
        ]

        resposta = self.gerar_resposta(mensagens_para_ia)

        turno_data = {
            "name": proximo.capitalize(), "text": resposta, "speaker": proximo,
            "position": "left" if random.random() > 0.5 else "right",
            "previous": self.ultimo_falante
        }

        if not pregenerate_next:
            self.historico.append({"falante": proximo, "texto": resposta})
            self.ultimo_falante = proximo
            self.turnos_por_falante[proximo] = self.turnos_por_falante.get(proximo, 0) + 1

        return turno_data


def executar_debate(tela, fontes, config_debate):
    running = True
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

    debate_over = False

    pauta_texto = PAUTAS_DEBATE.get(config_debate["pauta_titulo"], "Iniciando debate.")

    debate_simulator = DebateSimulator(config_debate["chave_openai"], config_debate["personagens"],
                                       config_debate["ordem_falantes"], pauta_texto)
    asset_manager = AssetManager()
    renderer = Renderer(tela, fontes["media"], fontes["grande"])
    dialogue_system = DialogueSystem(fontes["media"], SCREEN_WIDTH - 200)

    background_img = asset_manager.load_image("sala.png")
    character_imgs = {nome: asset_manager.load_image(f"{nome}.png", alpha=True) for nome in
                      config_debate["personagens"]}

    turnos_atuais = 1
    turnos_totais = config_debate["rodadas"] * len(config_debate["personagens"])

    current_turn = {
        "name": debate_simulator.ultimo_falante.capitalize(),
        "text": debate_simulator.historico[0]["texto"],
        "speaker": debate_simulator.ultimo_falante,
        "position": "left", "previous": None
    }
    dialogue_system.smart_wrap(current_turn["text"])

    debate_simulator.next_turn = debate_simulator.proximo_turno(pregenerate_next=True)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_PRINT, pygame.K_PRINTSCREEN]:
                renderer.save_screenshot()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c and (
                    pygame.key.get_mods() & pygame.KMOD_CTRL):
                if current_turn and not debate_over:
                    pyperclip.copy(current_turn["text"])
                    print("Texto copiado para a área de transferência!")

            elif event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                if debate_over:
                    if 'close_btn_rect' in locals() and close_btn_rect.collidepoint(pygame.mouse.get_pos()):
                        running = False
                    continue

                if not dialogue_system.is_page_complete():
                    dialogue_system.complete_current_page()
                elif dialogue_system.has_more_pages():
                    dialogue_system.next_page()
                else:
                    if turnos_atuais > turnos_totais:
                        debate_over = True
                        continue

                    pygame.mouse.set_cursor(*pygame.cursors.diamond)
                    pygame.display.flip()

                    try:
                        current_turn = debate_simulator.next_turn
                        if current_turn:
                            debate_simulator.historico.append(
                                {"falante": current_turn["speaker"], "texto": current_turn["text"]})
                            debate_simulator.ultimo_falante = current_turn["speaker"]
                            debate_simulator.turnos_por_falante[current_turn["speaker"]] = (
                                debate_simulator.turnos_por_falante.get(current_turn["speaker"], 0) + 1
                            )
                            dialogue_system.smart_wrap(current_turn["text"])

                            if turnos_atuais < turnos_totais:
                                debate_simulator.next_turn = debate_simulator.proximo_turno(pregenerate_next=True)
                            else:
                                debate_simulator.next_turn = None

                        turnos_atuais += 1

                    finally:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        # --- Renderização ---
        renderer.draw_background(background_img)

        # ATUALIZAÇÃO: Lógica de renderização corrigida para respeitar as rodadas
        if debate_over:
            close_btn_rect = renderer.draw_end_message()
        elif current_turn:
            renderer.draw_character(character_imgs[current_turn["speaker"]], current_turn["position"], darken=False,
                                    size=(300, 400))

            proximo_falante_data = debate_simulator.next_turn
            if proximo_falante_data:
                proximo_falante_nome = proximo_falante_data["speaker"]
                renderer.draw_character(
                    character_imgs[proximo_falante_nome],
                    "right" if current_turn["position"] == "left" else "left",
                    darken=True, size=(250, 350)
                )

            renderer.draw_text_box(
                name=current_turn["name"], text_lines=dialogue_system.get_current_text(),
                has_more_text=(not dialogue_system.is_page_complete() or dialogue_system.has_more_pages())
            )

        if current_turn and not dialogue_system.is_page_complete() and not debate_over:
            dialogue_system.update_typing()

        # ATUALIZAÇÃO: Adiciona um contador de turnos para depuração
        if not debate_over:
            turn_counter_text = f"Turno: {turnos_atuais - 1} / {turnos_totais}"
            counter_surface = fontes["pequena"].render(turn_counter_text, True, (255, 255, 255), (0, 0, 0))
            tela.blit(counter_surface, (10, 10))

        pygame.display.flip()
        clock.tick(60)

import pygame
import sys
import os
import pyperclip
import debate_core

pygame.init()

# --- Configurações iniciais ---
LARGURA, ALTURA = pygame.display.Info().current_w, pygame.display.Info().current_h
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("Jogo Integrado")

# Fontes e cores
fonte_grande = pygame.font.SysFont("Courier", 36, bold=True)
fonte_media = pygame.font.SysFont("Courier", 28, bold=True)
fonte_pequena = pygame.font.SysFont("Courier", 22, bold=True)

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
MARROM = (70, 40, 0)
BEGE = (250, 240, 200)
VERDE = (0, 180, 0)
CINZA = (200, 200, 200)
CINZA_ESCURO = (150, 150, 150)

# --- Variáveis Gerais ---
estado = "menu"
estado_anterior = "menu"
rodadas = 5
chave_openai = "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"
volume = 0.5
mostrar_combo = False
opcoes_combo = [
    "Deportação de Imigrantes Ilegais",
    "Voto Obrigatório Vs. Voto Facultativo",
    "Cotas Raciais e Sociais na Educação",
    "Impacto do Desenvolvimento Tecnológico"
]
tema_selecionado = opcoes_combo[0]
arrastando_volume = False


# --- Carregar imagens (menu) ---
def carregar_imagem(caminho):
    return pygame.image.load(os.path.join("assets", caminho))


fundo_sobre = pygame.transform.scale(carregar_imagem("protipo SOBRE.png"), (LARGURA, ALTURA))
fundo_menu = pygame.transform.scale(carregar_imagem("fundo menu.png"), (LARGURA, ALTURA))
moldura = pygame.transform.scale(carregar_imagem("moldura.png"), (300, 50))
moldura_volume = pygame.transform.scale(carregar_imagem("moldura volume.png"), (300, 50))
fundo_iniciar = pygame.transform.scale(carregar_imagem("protipo INICIARR.png"), (LARGURA, ALTURA))

BTN_CONFIRMAR_LARGURA = 180
moldura_confirmar_personagem = pygame.transform.scale(carregar_imagem("moldura volume.png"),
                                                      (BTN_CONFIRMAR_LARGURA, 40))

img_iniciar = pygame.transform.scale(carregar_imagem("iniciar.png"), (300, 90))
img_config = pygame.transform.scale(carregar_imagem("configuracoes.png"), (300, 90))
img_sobre = pygame.transform.scale(carregar_imagem("sobre.png"), (300, 90))

rect_iniciar = img_iniciar.get_rect(center=(LARGURA // 2, 320))
rect_config = img_config.get_rect(center=(LARGURA // 2, 430))
rect_sobre = img_sobre.get_rect(center=(LARGURA // 2, 540))

botao_voltar = pygame.Rect(50, ALTURA - 88, 300, 50)
botao_avancar = pygame.Rect(LARGURA - 350, ALTURA - 88, 300, 50)

largura_max_combo = 300
for op in opcoes_combo:
    largura_texto = fonte_pequena.size(op)[0] + 40
    if largura_texto > largura_max_combo:
        largura_max_combo = largura_texto

campo_pauta = pygame.Rect(LARGURA - largura_max_combo - 150, 250, largura_max_combo, 50)
campo_rodadas = pygame.Rect(LARGURA - largura_max_combo - 150, 400, 100, 50)
campo_chave = pygame.Rect(900, 250, 300, 50)
campo_volume = pygame.Rect(900, 400, 300, 50)

# ATUALIZAÇÃO: Seta direita movida um pouco mais para a direita
SETA_LARGURA = 50
SETA_ESPACO_ESQUERDA = 10
SETA_ESPACO_DIREITA = 60  # Aumentado de 10 para 20
botao_diminuir = pygame.Rect(campo_rodadas.x - SETA_LARGURA - SETA_ESPACO_ESQUERDA, campo_rodadas.y, SETA_LARGURA,
                             campo_rodadas.height)
botao_aumentar = pygame.Rect(campo_rodadas.right + SETA_ESPACO_DIREITA, campo_rodadas.y, SETA_LARGURA,
                             campo_rodadas.height)

input_ativo = None

# --- Seleção de personagens ---
professores = ["luciana", "luigi"]
alunos = ["carlos", "lucas", "mariana", "mateus", "vinicius", "sofia", "juliana"]
personalidades = {
    "luciana": {"curto": "Erudita e conservadora"}, "luigi": {"curto": "Articulado e progressista"},
    "sofia": {"curto": "Motivacional estilo 'coach'"}, "juliana": {"curto": "Gosta de evitar conflitos"},
    "mateus": {"curto": "Religioso e tranquilo"}, "vinicius": {"curto": "Realista e irônico"},
    "mariana": {"curto": "Conservadora e realista"}, "lucas": {"curto": "Progressista e reflexivo"},
    "carlos": {"curto": "Pragmático e irônico"}
}

imagens = {}
for nome in professores + alunos:
    try:
        img = carregar_imagem(f"{nome}.png").convert_alpha()
        imagens[nome] = pygame.transform.scale(img, (150, 150))
    except pygame.error:
        print(f"Erro ao carregar a imagem: {nome}.png. Verifique o nome do arquivo.")
        imagens[nome] = pygame.Surface((150, 150))

selecoes = {"professor": 0, "alunos": [0, 1, 2, 3]}
travados = {"professor": False, "alunos": [False, False, False, False]}
x_prof, y_prof = 175, 130
setas_prof = {"esq": pygame.Rect(115, y_prof + 55, 40, 40), "dir": pygame.Rect(350, y_prof + 55, 40, 40)}
botao_confirmar_prof = pygame.Rect(x_prof + (150 - BTN_CONFIRMAR_LARGURA) // 2, y_prof + 210, BTN_CONFIRMAR_LARGURA, 40)
setas_alunos, botoes_confirmar_alunos = [], []
for i in range(4):
    setas_alunos.append({"esq": pygame.Rect(0, 0, 40, 40), "dir": pygame.Rect(0, 0, 40, 40)})
    botoes_confirmar_alunos.append(pygame.Rect(0, 0, BTN_CONFIRMAR_LARGURA, 40))
pos_alunos_grid = [(620, 130), (1000, 130), (620, 390), (1000, 390)]


# --- Funções do Jogo ---

def limitar(x, minimo, maximo): return max(min(x, maximo), minimo)


def desenhar_menu():
    tela.blit(fundo_menu, (0, 0))
    tela.blit(img_iniciar, rect_iniciar)
    tela.blit(img_config, rect_config)
    tela.blit(img_sobre, rect_sobre)


def desenhar_iniciar():
    tela.blit(fundo_iniciar, (0, 0))
    tela.blit(moldura, (botao_voltar.x, botao_voltar.y))
    tela.blit(moldura, (botao_avancar.x, botao_avancar.y))
    texto_voltar = fonte_media.render("Voltar", True, PRETO)
    tela.blit(texto_voltar, texto_voltar.get_rect(center=botao_voltar.center))
    texto_avancar = fonte_media.render("Avançar", True, PRETO)
    tela.blit(texto_avancar, texto_avancar.get_rect(center=botao_avancar.center))
    tela.blit(fonte_media.render("Pauta:", True, PRETO), (campo_pauta.x - 150, campo_pauta.y + 10))

    moldura_pauta_ajustada = pygame.transform.scale(moldura, (campo_pauta.width, 50))
    tela.blit(moldura_pauta_ajustada, (campo_pauta.x, campo_pauta.y))
    tela.blit(fonte_pequena.render(tema_selecionado, True, PRETO), (campo_pauta.x + 20, campo_pauta.y + 15))

    tela.blit(fonte_media.render("Rodadas:", True, PRETO), (campo_rodadas.x - 180, campo_rodadas.y + 10))
    if not mostrar_combo:
        moldura_rodadas = pygame.transform.scale(moldura, (150, 50))
        tela.blit(moldura_rodadas, (campo_rodadas.x, campo_rodadas.y))
        tela.blit(fonte_media.render(str(rodadas), True, PRETO), (campo_rodadas.x + 65, campo_rodadas.y + 10))

        moldura_seta = pygame.transform.scale(moldura, (botao_diminuir.width, botao_diminuir.height))
        tela.blit(moldura_seta, botao_diminuir)
        tela.blit(moldura_seta, botao_aumentar)

        texto_diminuir = fonte_media.render("<", True, PRETO)
        texto_aumentar = fonte_media.render(">", True, PRETO)
        tela.blit(texto_diminuir, texto_diminuir.get_rect(center=botao_diminuir.center))
        tela.blit(texto_aumentar, texto_aumentar.get_rect(center=botao_aumentar.center))

    if mostrar_combo:
        moldura_combo_ajustada = pygame.transform.scale(moldura_volume, (campo_pauta.width, 50))
        for i, op in enumerate(opcoes_combo):
            r = pygame.Rect(campo_pauta.x, campo_pauta.y + (i + 1) * 50, campo_pauta.width, 50)
            tela.blit(moldura_combo_ajustada, r)
            tela.blit(fonte_pequena.render(op, True, PRETO), (r.x + 10, r.y + 10))


def desenhar_config():
    tela.blit(fundo_iniciar, (0, 0))
    if input_ativo == "chave": pygame.draw.rect(tela, VERDE, campo_chave, 3)
    tela.blit(moldura, (campo_chave.x, campo_chave.y))
    tela.blit(fonte_media.render("Chave OpenAI:", True, PRETO), (campo_chave.x - 230, campo_chave.y + 12))

    texto_visivel = chave_openai
    padding = 20
    max_width = campo_chave.width - padding

    while fonte_media.size(texto_visivel)[0] > max_width and len(texto_visivel) > 0:
        texto_visivel = texto_visivel[1:]

    tela.blit(fonte_media.render(texto_visivel, True, PRETO), (campo_chave.x + 10, campo_chave.y + 12))

    pygame.draw.rect(tela, (100, 100, 255), (
        campo_volume.x + 2, campo_volume.y + 2, int(volume * (campo_volume.width - 4)), campo_volume.height - 4))
    tela.blit(moldura_volume, (campo_volume.x, campo_volume.y))
    tela.blit(fonte_media.render("Volume:", True, PRETO), (campo_volume.x - 130, campo_volume.y + 12))
    tela.blit(moldura, (botao_voltar.x, botao_voltar.y))
    texto_voltar = fonte_media.render("Voltar", True, PRETO)
    tela.blit(texto_voltar, texto_voltar.get_rect(center=botao_voltar.center))


def desenhar_sobre():
    tela.blit(fundo_sobre, (0, 0))
    tela.blit(moldura, (botao_voltar.x, botao_voltar.y))
    texto_voltar = fonte_media.render("Voltar", True, PRETO)
    tela.blit(texto_voltar, texto_voltar.get_rect(center=botao_voltar.center))


def desenhar_texto(texto, x, y, fonte_=fonte_media, cor=PRETO):
    tela.blit(fonte_.render(texto, True, cor), (x, y))


def desenhar_seta(x, y, direcao, travado):
    cor = CINZA_ESCURO if travado else PRETO
    pontos = [(x + 30, y), (x, y + 20), (x + 30, y + 40)] if direcao == 'esq' else [(x, y), (x + 30, y + 20),
                                                                                    (x, y + 40)]
    pygame.draw.polygon(tela, cor, pontos)


def avancar_personagem(tipo, indice, direcao):
    global selecoes
    lista = professores if tipo == "professor" else alunos
    idx_atual = selecoes["professor"] if tipo == "professor" else selecoes["alunos"][indice]
    total = len(lista)

    alunos_selecionados = {selecoes["alunos"][j] for j in range(4) if j != indice}

    novo_idx = (idx_atual + direcao + total) % total

    if tipo == "professor":
        selecoes["professor"] = novo_idx
    else:
        tentativas = 0
        while novo_idx in alunos_selecionados and tentativas < len(alunos):
            novo_idx = (novo_idx + direcao + total) % total
            tentativas += 1
        selecoes["alunos"][indice] = novo_idx


def desenhar_selecao_personagens():
    tela.blit(fundo_iniciar, (0, 0))
    desenhar_texto("Seleção de Personagens", LARGURA // 2 - 200, 30, fonte_grande)
    nome_prof = professores[selecoes["professor"]]
    tela.blit(imagens[nome_prof], (x_prof, y_prof))
    pygame.draw.rect(tela, VERDE if travados["professor"] else PRETO, pygame.Rect(x_prof, y_prof, 150, 150), 3)
    desenhar_texto(nome_prof.capitalize(), x_prof + 75 - fonte_pequena.size(nome_prof)[0] // 2, y_prof + 155,
                   fonte_pequena)
    desenhar_texto(personalidades[nome_prof]["curto"],
                   x_prof + 75 - fonte_pequena.size(personalidades[nome_prof]["curto"])[0] // 2, y_prof + 180,
                   fonte_pequena)
    desenhar_seta(setas_prof["esq"].x, setas_prof["esq"].y, 'esq', travados["professor"])
    desenhar_seta(setas_prof["dir"].x, setas_prof["dir"].y, 'dir', travados["professor"])
    tela.blit(moldura_confirmar_personagem, botao_confirmar_prof)
    txt_conf_prof = fonte_pequena.render("Confirmar" if not travados["professor"] else "Desconfirmar", True, PRETO)
    tela.blit(txt_conf_prof, txt_conf_prof.get_rect(center=botao_confirmar_prof.center))

    for i in range(4):
        x, y = pos_alunos_grid[i]
        nome_aluno = alunos[selecoes["alunos"][i]]
        tela.blit(imagens[nome_aluno], (x, y))
        pygame.draw.rect(tela, VERDE if travados["alunos"][i] else PRETO, pygame.Rect(x, y, 150, 150), 3)
        desenhar_texto(nome_aluno.capitalize(), x + 75 - fonte_pequena.size(nome_aluno)[0] // 2, y + 155, fonte_pequena)
        desenhar_texto(personalidades[nome_aluno]["curto"],
                       x + 75 - fonte_pequena.size(personalidades[nome_aluno]["curto"])[0] // 2, y + 180, fonte_pequena)
        setas_alunos[i]["esq"].topleft, setas_alunos[i]["dir"].topleft = (x - 50, y + 55), (x + 170, y + 55)
        desenhar_seta(setas_alunos[i]["esq"].x, setas_alunos[i]["esq"].y, 'esq', travados["alunos"][i])
        desenhar_seta(setas_alunos[i]["dir"].x, setas_alunos[i]["dir"].y, 'dir', travados["alunos"][i])
        botoes_confirmar_alunos[i].topleft = (x + (150 - BTN_CONFIRMAR_LARGURA) // 2, y + 210)
        tela.blit(moldura_confirmar_personagem, botoes_confirmar_alunos[i])
        txt_conf_aluno = fonte_pequena.render("Confirmar" if not travados["alunos"][i] else "Desconfirmar", True, PRETO)
        tela.blit(txt_conf_aluno, txt_conf_aluno.get_rect(center=botoes_confirmar_alunos[i].center))

    total_selecionados = int(travados["professor"]) + sum(travados["alunos"])
    desenhar_texto(f"Selecionados: {total_selecionados} / 5", 130, ALTURA - 160)
    tela.blit(moldura, (botao_voltar.x, botao_voltar.y))
    tela.blit(fonte_media.render("Voltar", True, PRETO),
              fonte_media.render("Voltar", True, PRETO).get_rect(center=botao_voltar.center))
    tela.blit(moldura, (botao_avancar.x, botao_avancar.y))
    cor_avancar = PRETO if total_selecionados == 5 else CINZA_ESCURO
    tela.blit(fonte_media.render("Avançar", True, cor_avancar),
              fonte_media.render("Avançar", True, cor_avancar).get_rect(center=botao_avancar.center))


def lidar_clique_selecao(pos):
    global travados
    if botao_confirmar_prof.collidepoint(pos): travados["professor"] = not travados["professor"]
    if not travados["professor"]:
        if setas_prof["esq"].collidepoint(pos):
            avancar_personagem("professor", None, -1)
        elif setas_prof["dir"].collidepoint(pos):
            avancar_personagem("professor", None, 1)
    for i in range(4):
        if botoes_confirmar_alunos[i].collidepoint(pos): travados["alunos"][i] = not travados["alunos"][i]
        if not travados["alunos"][i]:
            if setas_alunos[i]["esq"].collidepoint(pos):
                avancar_personagem("aluno", i, -1)
            elif setas_alunos[i]["dir"].collidepoint(pos):
                avancar_personagem("aluno", i, 1)


def main():
    global estado, mostrar_combo, tema_selecionado, rodadas, chave_openai, volume, input_ativo, estado_anterior, arrastando_volume
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(), sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if estado == "menu":
                    if rect_iniciar.collidepoint(mouse_pos):
                        estado = "iniciar"
                    elif rect_config.collidepoint(mouse_pos):
                        estado_anterior, estado = estado, "config"
                    elif rect_sobre.collidepoint(mouse_pos):
                        estado_anterior, estado = estado, "sobre"
                elif estado == "iniciar":
                    if botao_voltar.collidepoint(mouse_pos):
                        estado = "menu"
                    elif botao_avancar.collidepoint(mouse_pos):
                        estado = "selecionar_personagem"
                    elif campo_pauta.collidepoint(mouse_pos):
                        mostrar_combo = not mostrar_combo
                    elif not mostrar_combo and botao_diminuir.collidepoint(mouse_pos):
                        rodadas = limitar(rodadas - 1, 5, 10)
                    elif not mostrar_combo and botao_aumentar.collidepoint(mouse_pos):
                        rodadas = limitar(rodadas + 1, 5, 10)
                    elif mostrar_combo:
                        for i, op in enumerate(opcoes_combo):
                            r = pygame.Rect(campo_pauta.x, campo_pauta.y + (i + 1) * 50, campo_pauta.width, 50)
                            if r.collidepoint(mouse_pos):
                                tema_selecionado, mostrar_combo = op, False
                elif estado == "config":
                    if botao_voltar.collidepoint(
                            mouse_pos): estado, input_ativo, arrastando_volume = estado_anterior, None, False
                    if campo_chave.collidepoint(mouse_pos):
                        input_ativo, arrastando_volume = "chave", False
                    elif campo_volume.collidepoint(mouse_pos):
                        input_ativo, arrastando_volume = "volume", True
                        volume = limitar((mouse_pos[0] - campo_volume.x) / campo_volume.width, 0, 1)
                    else:
                        input_ativo, arrastando_volume = None, False
                elif estado == "sobre":
                    if botao_voltar.collidepoint(mouse_pos): estado = estado_anterior
                elif estado == "selecionar_personagem":
                    if botao_voltar.collidepoint(mouse_pos):
                        estado = "iniciar"
                    elif botao_avancar.collidepoint(mouse_pos) and (
                            int(travados["professor"]) + sum(travados["alunos"])) == 5:
                        nome_professor = professores[selecoes["professor"]]
                        nomes_alunos = [alunos[idx] for idx in selecoes["alunos"]]
                        config = {
                            "chave_openai": chave_openai, "rodadas": rodadas,
                            "pauta_titulo": tema_selecionado,
                            "personagens": [nome_professor] + nomes_alunos,
                            "ordem_falantes": [nome_professor] + nomes_alunos,
                        }
                        fontes = {"grande": fonte_grande, "media": fonte_media, "pequena": fonte_pequena}
                        debate_core.executar_debate(tela, fontes, config)
                        estado = "menu"
                    else:
                        lidar_clique_selecao(mouse_pos)
            elif event.type == pygame.MOUSEMOTION and estado == "config" and arrastando_volume:
                volume = limitar((event.pos[0] - campo_volume.x) / campo_volume.width, 0, 1)
            elif event.type == pygame.MOUSEBUTTONUP and estado == "config":
                arrastando_volume = False
            elif event.type == pygame.KEYDOWN and estado == "config" and input_ativo == "chave":
                mods = pygame.key.get_mods()
                if event.key == pygame.K_v and (mods & pygame.KMOD_CTRL or mods & pygame.KMOD_META):
                    chave_openai = (chave_openai + pyperclip.paste())
                elif event.key == pygame.K_BACKSPACE:
                    chave_openai = chave_openai[:-1]
                else:
                    if event.unicode.isprintable():
                        chave_openai += event.unicode

        tela.fill(BRANCO)
        if estado == "menu":
            desenhar_menu()
        elif estado == "iniciar":
            desenhar_iniciar()
        elif estado == "config":
            desenhar_config()
        elif estado == "sobre":
            desenhar_sobre()
        elif estado == "selecionar_personagem":
            desenhar_selecao_personagens()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
import math
from multiprocessing import Process, Queue
import pygame
import pygame_gui.elements

from engine.AIEngine import AIEngine
from src.GameInit import GameInit
from src.config import *

class PlayAIVsAIMode(GameInit):
    def __init__(self):
        super().__init__()
        self.aiTurn = 'b'  # Đen đi trước
        self.aiEngine_black = AIEngine('b')  # Đen dùng AlphaBeta
        self.aiEngine_white = AIEngine('w')  # Trắng dùng Minimax
        self.screen = pygame.display.set_mode((WIDTH_WINDOW_AI, HEIGHT_WINDOW_AI))
        self.manager.set_window_resolution((WIDTH_WINDOW_AI, HEIGHT_WINDOW_AI))
        self.running = True
        self.gameOver = False
        self.moveMade = False
        self.signal = True
        self.clock = pygame.time.Clock()
        self.q = Queue()
        self.find_move_process = None
        self.time_delta = 0
        self.move_log_white = []
        self.move_log_black = []
        # Xóa panel cũ của GameInit
        if hasattr(self, 'chess_panel'):
            self.chess_panel.hide()
        self.__loadGUIAIvsAI()

    def __loadGUIAIvsAI(self):
        # Chỉ tạo 1 panel tổng hợp, hiển thị thông tin cho cả 2 bên
        panel_width = WIDTH_AI - 20
        panel_height = HEIGHT_AI - 20
        panel_x = LEFT_PANEL + 10
        panel_y = 10
        self.ai_panel = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((panel_x, panel_y), (panel_width, panel_height)),
            manager=self.manager,
            window_display_title='AI vs AI Info',
            draggable=False
        )
        self.text_box = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 10), (panel_width - 20, panel_height - 20)),
            html_text='',
            manager=self.manager,
            container=self.ai_panel
        )
        self.updateAIPanel()

    def updateAIPanel(self):
        # Thông tin thuật toán
        algo_info = (
            f"<b>White:</b> Minimax | <b>Black:</b> Alpha Beta<br>"
        )
        # Lấy các nước đi dạng bảng
        white_moves = [m.getChessNotation() for m in self.gs.moveLog if m.movePiece[0] == 'w']
        black_moves = [m.getChessNotation() for m in self.gs.moveLog if m.movePiece[0] == 'b']
        max_len = max(len(white_moves), len(black_moves))
        rows = []
        rows.append(f"<b>{'No.':<4}{'White':<8}{'Black':<8}</b>")
        for i in range(max_len):
            w = white_moves[i] if i < len(white_moves) else ''
            b = black_moves[i] if i < len(black_moves) else ''
            rows.append(f"{i+1:<4}{w:<8}{b:<8}")
        moves_table = '<br>'.join(rows)
        # Thông tin lượt, possible moves, in check
        turn = 'White' if self.gs.turn == 'w' else 'Black'
        possible_moves = len(self.gs.getValidMoves())
        in_check = self.gs.inCheck
        status = f"<b>Turn:</b> {turn} | <b>Possible moves:</b> {possible_moves} | <b>In Check:</b> {in_check}<br>"
        # Kết hợp và cập nhật panel
        html = algo_info + status + '<pre>' + moves_table + '</pre>'
        self.text_box.set_text(html)

    def mainLoop(self):
        while self.running:
            self.time_delta = self.clock.tick(MAX_FPS) / 1000
            self.__eventHandler()
            if not self.gameOver and self.signal:
                self.__AIvsAIProcess()
            if self.moveMade:
                self.validMoves = self.gs.getValidMoves()
                if len(self.validMoves) == 0:
                    self.gameOver = True
                    self.showEndGameDialog()
                self.moveMade = False
                self.signal = True
                self.updateAIPanel()
            self.manager.update(self.time_delta)
            self.drawGameScreen()
            pygame.display.update()

    def showEndGameDialog(self):
        # Xác định kết quả
        if not self.gs.inCheck:
            result = "Draw!"
        elif self.gs.turn == 'w':
            result = "Black wins!"
        else:
            result = "White wins!"
        # Hiển thị dialog
        self.endgame_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((WIDTH // 2 - 120, HEIGHT // 2 - 60), (240, 120)),
            manager=self.manager,
            window_display_title='Game Over',
            resizable=False,
            draggable=False
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 30), (200, 40)),
            text=result,
            manager=self.manager,
            container=self.endgame_window
        )
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((70, 80), (100, 30)),
            text='OK',
            manager=self.manager,
            container=self.endgame_window,
            object_id='#endgame_ok'
        )

    def __AIvsAIProcess(self):
        ai_color = 'b' if self.gs.turn == 'b' else 'w'
        if ai_color == 'b':
            # Đen dùng AlphaBeta
            self.find_move_process = Process(target=self.aiEngine_black.AlphaBetaPruning,
                                             args=(self.gs, DEPTH, -math.inf, math.inf, self.q))
        else:
            # Trắng dùng Minimax
            self.find_move_process = Process(target=self.aiEngine_white.MiniMax,
                                             args=(self.gs, DEPTH, self.q))
        self.find_move_process.start()
        self.find_move_process.join()
        ai_engine = self.q.get()
        if ai_engine.bestMove:
            self.gs.makeMove(ai_engine.bestMove)
        self.moveMade = True
        self.signal = False

    def __eventHandler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if hasattr(self, 'endgame_window') and event.ui_element == self.endgame_window.get_element('#endgame_ok'):
                        self.running = False
            self.manager.process_events(event)

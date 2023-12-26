import math
import os
import random
import sys
import time
from typing import Any
import pygame as pg
from pygame.sprite import AbstractGroup


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

def check_bound(obj: pg.Rect) -> tuple[bool, bool]:

    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm
def sound():
        pg.mixer.init()    # 初期設定
         
        pg.mixer.music.load("ex05/encount.mp3")     # 音楽ファイルの読み込み
        
        pg.mixer.music.play(-1)#無限再生
         
        #time.sleep(100)
        #pg.mixer.music.stop()               # 再生の終了
def boss_sound():
    pg.mixer.init()    # 初期設定
         
    pg.mixer.music.load("ex05/boudou.mp3")     # 音楽ファイルの読み込み
        
    pg.mixer.music.play(-1)#無限再生





class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "nomal"
        self.hyper_life = -1

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        if num == 10:  #numが10番の画像(七面鳥の画像)の時
            self.image = pg.transform.scale(self.image, (200, 115))  #サイズ変更
        screen.blit(self.image, self.rect)

    def change_state(self, state: str, hyper_life: int):
        """
        引数1 state:こうかとんの状態
        引数2 hyper_life:こうかとんのハイパー状態
        """
        self.state = state
        self.hyper_life = hyper_life

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        if self.state == "hyper":
            self.image = pg.transform.laplacian(self.image)
            self.hyper_life -= 1
        if self.hyper_life < 0:
            self.change_state("nomal", -1)
        screen.blit(self.image, self.rect)

class Bird2(pg.sprite.Sprite):
    """
    もう一体のこうかとんに関するクラス
    """
    delta = {   # wasdの辞書
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        もう一体のこうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)
        self.imgs = {
            (+1, 0): img,
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),
            (-1, 0): img0,
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "nomal"
        self.hyper_life = -1

    def change_img(self, num: int, screen: pg.Surface):
        """
        もう一体のこうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def change_state(self, state: str, hyper_life: int):
        """
        引数1 state:こうかとんの状態
        引数2 hyper_life:こうかとんのハイパー状態
        """
        self.state = state
        self.hyper_life = hyper_life

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてもう一体のこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        if self.state == "hyper":
            self.image = pg.transform.laplacian(self.image)
            self.hyper_life -= 1
        if self.hyper_life < 0:
            self.change_state("nomal", -1)
        screen.blit(self.image, self.rect)



class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
            

class Fire(pg.sprite.Sprite):
    """
    火に関するクラス
    """

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        火画像Surfaceを生成する
        """
        super().__init__()
        self.image = pg.image.load(f"{MAIN_DIR}/fig/fire.png")
        self.image = pg.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()
        # 火を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 10

    def update(self):
        """
        火を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird,angle: int = 0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        rotated_image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam.png"), angle, 2.0)
        self.image = pg.transform.flip(rotated_image, False, True)
        angle = math.degrees(math.atan2(-self.vy, self.vx)) + angle
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

class NeoBeam():
    """
    新しいビームに関するクラス
    """
    def __init__(self, bird: Bird, num: int):
        """
        新しいビームを生成する
        引数1 bird：ビームを発射するこうかとん
        引数2 num：ビーム数
        """
        self.bird = bird
        self.num = num

    def gen_beams(self) -> list[Beam]:
        
        angles = range(-50, 51, int(100 / (self.num - 1)))  # ビームの角度を計算
        beams = []
        for angle in angles:
            beams.append(Beam(self.bird, angle))
        return beams
    
class Beam2(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird2: Bird2, angle: int = 0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん2
        """
        super().__init__()
        self.vx, self.vy = bird2.dire
        rotated_image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam.png"), angle, 2.0)
        self.image = pg.transform.flip(rotated_image, False, True)
        angle = math.degrees(math.atan2(-self.vy, self.vx)) + angle
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird2.rect.centery+bird2.rect.height*self.vy
        self.rect.centerx = bird2.rect.centerx+bird2.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()

class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"{MAIN_DIR}/fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"{MAIN_DIR}/fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, HEIGHT/2)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy

class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 400
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

class Life:
    """
    ライフの表示とゲームオーバー画面を表示するクラス
    初期のライフ数: 3
    """
    def __init__(self):
        """"
        初期ライフ数を画面に表示
        """
        self.font = pg.font.Font(None, 60)
        self.color = (255, 0, 0)
        self.life = 3
        self.image = self.font.render(f"Life: {self.life}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 1500, HEIGHT-50

    def update(self, screen: pg.Surface):
        """"
        爆弾と衝突した際にライフを減らして更新する
        引数 screen:画面Surface
        """
        self.image = self.font.render(f"Life: {self.life}", 0, self.color)
        screen.blit(self.image, self.rect)

    def gameover(self, screen: pg.Surface):
        screen.fill((0, 0, 0))
        self.font = pg.font.Font(None, 100)
        self.text = self.font.render("GameOver", True, (255, 255, 255))
        screen.blit(self.text, (650, HEIGHT/2))
        


class Boss(pg.sprite.Sprite):
    """
    ボスに関するクラス
    """

    def __init__(self):
        super().__init__()
        """
        ボスについて
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/Boss.png"), 0, 0.4)
        self.rect = self.image.get_rect()
        self.rect.center = 100,random.randint(100, 200)
        self.vy = +6
        self.bound = random.randint(230, HEIGHT/2)
        self.state = "move" # 降下状態or停止状態
    
    def update(self):
        """
        Bossを速度ベクトルself.vyに基づき移動させる
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy


class BossFont(pg.sprite.Sprite):
     def __init__(self):
        """
        Boss出現フォントに関するクラス
        """
        super().__init__()
        self.font = pg.font.Font(None, 100)
        self.color = (255, 0, 0)
        self.image = self.font.render("=BOSS=", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH/2, HEIGHT/2


class BossBomb(pg.sprite.Sprite):
    """
    Bossの爆弾に関するクラス
    """
    def __init__(self, boss: "Boss", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 boss：爆弾を飛ばすBoss
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = 15 #半径
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, (0, 255, 255), (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するBossから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(boss.rect, bird.rect)  
        self.rect.centerx = boss.rect.centerx
        self.rect.centery = boss.rect.centery
        self.speed = 10 #爆弾速度設定

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Clear(pg.sprite.Sprite):
    """
    クリア画面
    """
    def __init__(self):
        self.life = 1
        self.font = pg.font.Font(None, 60)
        self.color = (255, 0, 0)
        self.image = self.font.render(f"Life: {self.life}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 1500, HEIGHT-50

    def update(self, screen: pg.surface):
        self.image = self.font.render(f"Life: {self.life}", 0, self.color)
        screen.blit(self.image, self.rect)

    def last(self, screen: pg.Surface):
        self.size = 200
        screen.fill((255, 255, 255))
        self.font = pg.font.Font(None, self.size)
        self.clear_text = self.font.render("CLEAR!", True, (255, 0, 0))
        screen.blit(self.clear_text, (WIDTH/2-self.size, HEIGHT/2))






def main():
    
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    score = Score()
    boss_font = BossFont()
    clear = Clear()
    life = Life()
    sound()
    bird = Bird(3, (900, 400))
    bird2 = Bird2(3, (700, 400))  # もう一体のこうかとんを生成
    bombs = pg.sprite.Group()
    fires = pg.sprite.Group()
    beams = pg.sprite.Group()
    beams2 = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    bosss = pg.sprite.Group()
    

    tmr = 0
    clock = pg.time.Clock()
    boss_font_spawned = False #Boss出現文字列を表示したか
    boss_spawned = False #Bossが出現したか
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if pg.key.get_mods() & pg.KMOD_LSHIFT:
                    beams.add(NeoBeam(bird, num=5).gen_beams())   # 5本のビームを生成
                else:
                    beams.add(Beam(bird))
                beams2.add(Beam2(bird2))
                    

        # for event in pg.event.get():
        #     if event.type == pg.QUIT:
        #         return 0
        #     if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
        #         beams2.add(Beam2(bird2))

            if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT:
                if score.value >= 100 and boss_spawned == False: #bossが出現しているときはnomal状態
                    bird.change_state("hyper", 500)
                    score.value -= 100
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                bird.speed = 20
            if event.type == pg.KEYDOWN and event.key != pg.K_LSHIFT:
                bird.speed = 10
            if event.type == pg.KEYDOWN and event.key == pg.K_l:
                if score.value >= 500:  # スコアが500以上ならば
                    life.life += 1  # ライフを1つ追加する
                    score.value -= 500

            
        
        screen.blit(bg_img, [0, 0])
        

        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())
            
        if score.value >= 500 and not boss_spawned: #スコアが500以上かつBossがまだ出現していなければ
            time.sleep(1) #ボスが出現で1秒間止まる
            bosss.add(Boss()) #ボス出現
            boss_spawned = True #ボスを出現したにする
            boss_font_spawned = True
            boss_sound() 
            

        if boss_spawned == True: #Bossが出現したらnomal状態に戻る
            bird.hyper_life = -1 #ボス出現中はhyper状態禁止(nomal状態)
            bird.state == "nomal"

        if boss_font_spawned == True: #ボス出現時文字列が表示されたら
            span = tmr%50
            if 0 <= span < 25: #文字列点滅
                boss_font_instance = BossFont()
                screen.blit(boss_font_instance.image, boss_font_instance.rect) #文字列生成

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(emy, bird))
            if tmr%200 == 0:  # 200フレームに1回，火を出現させる
                    fires.add(Fire(emy, bird))

    

        for boss in bosss: 
            if boss.state == "stop" and tmr%30 == 0:
                # Bossが停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(BossBomb(boss, bird))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            # pg.mixer.music.stop()
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 100  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for boss in pg.sprite.groupcollide(bosss, beams, True, True).keys(): #ボスが倒されたら
            exps.add(Explosion(boss, 100)) # 爆発エフェクト
            score.value += 500 # 500点アップ
            bird.change_img(6, screen) # こうかとん喜びエフェクト
            boss_font_spawned = False #文字列を消す
            clear.life -= 1
            if clear.life == 0:
                clear.last(screen)
                pg.display.update()
                time.sleep(4)
                return
            
        for emy in pg.sprite.groupcollide(emys, beams2, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 100  # 10点アップ
            bird2.change_img(6, screen)  # こうかとん喜びエフェクト

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
            
           

        for fire in pg.sprite.groupcollide(fires, beams, True, True).keys():
            exps.add(Explosion(fire, 50))  # 火エフェクト
            score.value += 100  # 100点アップ
        for bomb in pg.sprite.groupcollide(bombs, beams2, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ


        for bomb in pg.sprite.spritecollide(bird, bombs, True):
            if bird.state == "hyper":
                exps.add(Explosion(bomb,50))
                score.value += 1
            else:
                life.life -= 1  # こうかとんと爆弾が衝突したら、ライフを1つ減らす
                if life.life == 0:  # もし、ライフが0になったら
                    life.gameover(screen)
                    pg.display.update()
                    time.sleep(2)
                    return
            
        for fire in pg.sprite.spritecollide(bird, fires, True):
            if bird.state == "hyper":
                exps.add(Explosion(fire,50))
                score.value += 1
            else:
                bird.change_img(10, screen) # 七面鳥エフェクト
                score.update(screen)
                pg.display.update()
                time.sleep(1)
                life.gameover(screen)
                pg.display.update()
                time.sleep(2)
                return

        bird.update(key_lst, screen)
        bird2.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        beams2.update()
        beams2.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        fires.update()
        fires.draw(screen)
        exps.update()
        exps.draw(screen)
        bosss.update()
        bosss.draw(screen)
        score.update(screen)
        boss_font.update(screen)
        life.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)
        
if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
   

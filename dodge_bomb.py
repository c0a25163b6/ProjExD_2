import os
import sys
import pygame as pg
import math
import random

#修正画面サイズ変更なし
WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#練習３：画面制限詳細
def check_bound(obj_rect: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectかばくだんRect
    戻り値：タプル（横方向判定結果，縦方向判定結果）
    画面内ならTrue，画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rect.left < 0 or WIDTH < obj_rect.right:
        yoko = False        
    if obj_rect.top < 0 or HEIGHT < obj_rect.bottom:
        tate = False
    return yoko, tate

#演習問題１：ゲームオーバー関数
def game_over(screen: pg.Surface) -> None:
    #黒背景作成
    scr = pg.Surface((WIDTH, HEIGHT))
    scr.fill((0, 0, 0))
    scr.set_alpha(220)

    #文字の表示
    font = pg.font.Font(None, 80)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rct = text.get_rect()
    text_rct.center = WIDTH // 2, HEIGHT // 2

    #左のこうかとん
    scr.blit(text, text_rct)
    gok_img = pg.image.load("fig/8.png") 
    gok_rct = gok_img.get_rect()
    gok_rct.center =  WIDTH / 2 - 200 , HEIGHT / 2  #位置を修正
    scr.blit(gok_img, gok_rct)
    #右のこうかとん
    gok_rct2 = gok_img.get_rect()
    gok_rct2.center = WIDTH / 2 + 200 , HEIGHT / 2 #位置を修正
    scr.blit(gok_img, gok_rct2)

    screen.blit(scr, [0, 0])
    #時間の設定
    pg.display.update()
    clock = pg.time.Clock()
    clock.tick(0.2)

#演習課題２：加速度関数
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = [] #爆弾用のリスト

    #上昇段階は10段階
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        
        bb_img.set_colorkey((0, 0, 0)) 
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
        
    bb_accs = [a * 0.5 for a in range(1, 11)] #加速度のリスト
    
    return bb_imgs, bb_accs

#追加機能３：こうかとんの向き変更
def init_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    kk_img = pg.image.load("fig/3.png")
    kkd_img = pg.image.load("fig/6.png")
    kk_dict = {} #角度の辞書
    kk_move = [ #移動向きのリスト
        (-5, 0),
        (-5, -5),
        (0, -5),
        (+5, -5),
        (+5, 0),
        (+5, +5),
        (0, +5),
        (-5, +5),
    ]

    kk_dict[(0, 0)] = pg.transform.rotozoom(kk_img, 0, 0.9) #標準時は左向き

    for i, m in enumerate(kk_move):
        if m[0] > 0: #右向きの時は反転させて角度を調整
            ck_img = pg.transform.flip(kk_img, True, False)
            angle = -(i - 4) * 45
        else: #それ以外は通常のものを使用
            ck_img = kk_img
            angle = -i * 45
        kk_dict[m] = pg.transform.rotozoom(ck_img, angle, 0.9)

        #ダッシュ時用（追加課題5用）
        if m[0] > 0:
            dk_img = pg.transform.flip(kkd_img, True, False)
            d_angle = -(i - 4) * 45
        else: #それ以外は通常のものを使用
            dk_img = kkd_img
            d_angle = -i * 45
        dash_m = (m[0] * 5, m[1] * 5)
        kk_dict[dash_m] = pg.transform.rotozoom(dk_img, d_angle, 0.9)

    return kk_dict 

#追加機能４：カウントダウン(タイマー)
def game_time(screen: pg.Surface, tmr: int) -> None:
    font = pg.font.Font(None, 40)
    s = tmr // 50
    timer = font.render(f"{s}", True, (255, 255, 255))
    screen.blit(timer, [WIDTH // 2, 10])

#追加機能５：ダッシュモード
def act_dash(key_lst: list[bool], tmr: int, dash: int, sum_mv: list[int]) -> tuple[int, list[int]]:
    if key_lst[pg.K_SPACE] and (tmr - dash > 150):
        dash = tmr
    if tmr - dash < 5:
        sum_mv[0] *= 5
        sum_mv[1] *= 5
    return dash, sum_mv

#追加機能６：追従型機能
def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    dx = org[0] - dst[0]
    dy = org[1] - dst[1]
    dist = math.sqrt(dx * dx + dy * dy) or 300
    
    #正規化
    x = (dx / dist) * 5 
    y = (dy / dist) * 5
    current_xy  = (x, y)
    return x, y

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    

    kk_imgs = init_kk_imgs()
    
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    clock = pg.time.Clock()

    #練習１：辞書の定義
    DELTA = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    #練習２：赤い爆弾を作成
    bb_imgs, bb_accs = init_bb_imgs()

    vx, vy = +5, +5
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = 400, 300

    #追加課題6用（青色爆弾）
    bb_img_h = pg.Surface((20, 20))
    pg.draw.circle(bb_img_h, (0, 0, 255), (10, 10), 10)
    bb_img_h.set_colorkey((0, 0, 0))

    bb_rct_h = bb_img_h.get_rect()
    hvx, hvy = +5, +5

    tmr = 0
    dash_tmr = -150
    damage_tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return

        screen.blit(bg_img, [0, 0])

        #タイマー設置
        time = tmr // 50
        game_time(screen, tmr)

        #練習１：辞書の情報を取り出す
        sum_mv = [0, 0]
        key_lst = pg.key.get_pressed()

        if damage_tmr > 0:
            damage_tmr -= 1
        else:
            for key, mv in DELTA.items():
                if key_lst[key]:
                    sum_mv[0] += mv[0]
                    sum_mv[1] += mv[1]

            dash_tmr, sum_mv = act_dash(key_lst, tmr, dash_tmr, sum_mv)
                
        kk_rct.move_ip(sum_mv)
        #ここで辞書を使う
        kk_img = kk_imgs[tuple(sum_mv)]

        #練習３：横または縦で端っこにいるなら動けなくする
        y_kk, t_kk = check_bound(kk_rct)
        if y_kk == False or t_kk == False:
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        #先にiで獲得しておく
        i = min(tmr //500, 9)
        bb_img = bb_imgs[i]
        #画像サイズ
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        #画像のでかさ
        avx = vx *  bb_accs[i]
        avy = vy *  bb_accs[i]

       #練習３：端っこにぶつかったら反射させる
        bb_rct.move_ip(avx, avy)
        y_bb, t_bb = check_bound(bb_rct)
        if y_bb == False:
            vx *= -1
        if t_bb == False:
            vy *= -1
        screen.blit(bb_img, bb_rct)

        #追加機能6用
        if time >= 10:
            bb_rct_h.move_ip(hvx, hvy)
            hvx, hvy = calc_orientation(kk_rct, bb_rct_h, (hvx , hvy))
            screen.blit(bb_img_h, bb_rct_h)

        #練習４：衝突したら終了する
        if kk_rct.colliderect(bb_rct):
            game_over(screen) #ここで呼び出す
            return

        if kk_rct.colliderect(bb_rct_h): #ホーミング用
            if damage_tmr == 0:
                damage_tmr = 50  #1秒間
                bb_rct_h.center = random.randint(0, 1100), random.randint(0, 650)  #ホーミングをランダムにリセット


        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
import os
import sys
import pygame as pg
import time

#練習３：画面サイズを変更
WIDTH, HEIGHT = 800, 600
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
    gok_rct.center =  200, 300
    scr.blit(gok_img, gok_rct)
    #右のこうかとん
    gok_rct2 = gok_img.get_rect()
    gok_rct2.center = 600, 300
    scr.blit(gok_img, gok_rct2)

    screen.blit(scr, [0, 0])
    #時間の設定
    pg.display.update()
    time.sleep(5)

#演習課題２
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

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
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

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return

        screen.blit(bg_img, [0, 0]) 
        #練習１：辞書の情報を取り出す
        sum_mv = [0, 0]
        key_lst = pg.key.get_pressed()
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
                
        kk_rct.move_ip(sum_mv)

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

        #練習４：衝突したら終了する
        if kk_rct.colliderect(bb_rct):
            game_over(screen) #ここで呼び出す
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
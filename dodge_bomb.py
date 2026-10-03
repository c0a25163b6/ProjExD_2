import os
import sys
import pygame as pg

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
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))

    bb_rct = bb_img.get_rect()
    bb_rct.center = 500, 300

    #練習２：初期値座標
    vx = +5
    vy = +5

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

       #練習３：端っこにぶつかったら反射させる
        bb_rct.move_ip(vx, vy)
        y_bb, t_bb = check_bound(bb_rct)
        if y_bb == False:
            vx *= -1
        if t_bb == False:
            vy *= -1
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

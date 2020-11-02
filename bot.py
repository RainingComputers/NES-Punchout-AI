#!/usr/bin/python3 

import os
import time
import multiprocessing as mp

import cv2
import mss
import numpy as np

import pykitml as pk

import pygame
import pygame.freetype

# Values shared between processess
A_val = mp.Value('d', 0)
left_val = mp.Value('d', 0) 

# Initialize pygame
pygame.init()
infoObject = pygame.display.Info()
display = pygame.display.set_mode((500, 400))
pygame.display.set_caption('Mac AI')
font = pygame.font.SysFont('courier', 16, bold=1)

# Initialize labels
inp_txt = font.render('inp', True, pygame.Color('white'))
pca_txt = font.render('pca', True, pygame.Color('white'))
z_txt = font.render('z', True, pygame.Color('white'))
i_txt = font.render('i', True, pygame.Color('white'))
f_txt = font.render('f', True, pygame.Color('white'))
o_txt = font.render('o', True, pygame.Color('white'))
c_txt = font.render('c', True, pygame.Color('white'))
y_txt = font.render('y', True, pygame.Color('white'))
out_txt = font.render('out', True, pygame.Color('white'))

def on_frame(server, frame, A_val, left_val): 
    # Toggle start button to start rounds
    if(frame%10 < 5): start = True
    else: start = False

    # Set joypad
    server.set_joypad(A=A_val.value==1, left=left_val.value==1, start=start)

    # Continue emulation
    server.frame_advance()

def gray(im):
    # Normalize numpy array between 0 and 255
    im = 255 * (im / im.max())
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret

def np2surf(arr, scale):
    # Convert numpy array to pygame surface
    if(arr.ndim == 1):
        surf = pygame.surfarray.make_surface(gray(np.array([arr])))
        surf = pygame.transform.scale(surf, scale) 
        surf = pygame.transform.rotate(surf, 90)  
    else:
        surf = pygame.surfarray.make_surface(gray(arr.T))
        surf = pygame.transform.scale(surf, scale) 

    return surf

def show_model(img_surf, pca_surf, model, dps):
    # Clear screen
    display.fill(pygame.Color('black'))

    # Display descision/sec
    dps_str = f'dps = {dps}'
    dps_txt = font.render(dps_str, True, pygame.Color('white'))
    display.blit(dps_txt, (330, 10))

    # Display labels
    display.blit(inp_txt, (15, 10))
    display.blit(pca_txt, (15, 160))
    display.blit(z_txt, (35, 190))
    display.blit(i_txt, (35, 220))
    display.blit(f_txt, (35, 250))
    display.blit(o_txt, (35, 280))
    display.blit(c_txt, (35, 310))
    display.blit(y_txt, (35, 340))
    display.blit(out_txt, (15, 370))

    # Convert model activations to pygame surfaces
    t = model.t-1
    z_surf = np2surf(model.z[1][t].reshape((2, 50)), (400, 16))
    i_surf = np2surf(model.i[1][t].reshape((2, 50)), (400, 16))
    f_surf = np2surf(model.f[1][t].reshape((2, 50)), (400, 16))
    o_surf = np2surf(model.o[1][t].reshape((2, 50)), (400, 16))
    c_surf = np2surf(model.c[1][t].reshape((2, 50)), (400, 16))
    y_surf = np2surf(model.y[1][t].reshape((2, 50)), (400, 16))
    out_surf = np2surf(model.out_a[t], (16, 48))

    # Draw numpy arrays
    display.blit(img_surf, (55, 10))
    display.blit(pca_surf, (55, 160))
    display.blit(z_surf, (55, 190))
    display.blit(i_surf, (55, 220))
    display.blit(f_surf, (55, 250))
    display.blit(o_surf, (55, 280))
    display.blit(c_surf, (55, 310))
    display.blit(y_surf, (55, 340))
    display.blit(out_surf, (55, 370))

    # Draw borders
    pygame.draw.rect(display, (255, 0, 0), (54, 9, 130, 130), 1)
    pygame.draw.rect(display, (255, 0, 0), (54, 159, 258, 18), 1)
    for i in range(1, 7):
        pygame.draw.rect(display, (255, 0, 0), (54, 159+30*i, 402, 18), 1)
    pygame.draw.rect(display, (255, 0, 0), (54, 369, 50, 18), 1)


# Initialize and start server
def start_server(A_val, left_val):
    server = pk.FCEUXServer(lambda server, frame: on_frame(server, frame, A_val, left_val))
    print(server.info)
    server.start()

if __name__ == '__main__':
    p = mp.Process(target=start_server, args=(A_val, left_val))
    p.start()

    # Load models
    pca = pk.load('pca.pkl')
    model = pk.load('best.pkl')
    last_render = time.time()
    dps = 0

    with mss.mss() as sct:
        # Part of the screen to capture (1548, 203, 256, 256) for 1080p screen
        monitor = {"top": 203, "left": infoObject.current_w-256-116, "width": 256, "height": 256}

        running = True
        while running:    
            last_time = time.time()

            # Get raw pixels from the screen, save it to a Numpy array
            img = np.array(sct.grab(monitor))
            # Convert to gray scale
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            # Resize image
            img = cv2.resize(src=img, dsize=(64, 64))
            img_surf = np2surf(img, (128, 128))
            # Reshape
            img = img.reshape(4096)
            # Normalize
            img = img/255

            # PCA
            img = pca.transform(img)
            pca_surf = np2surf(img.reshape(2, 32), (256, 16))
            # Feed to model
            model.feed(img)
            A_val.value, left_val.value, _ = model.get_output_onehot()

            # Render model visualization, limit to 30fps
            if(time.time() - last_render > 1/30):
                # Render visualization
                last_render = time.time()
                show_model(img_surf, pca_surf, model, round(dps, 2))
                pygame.display.update()

                # Handle quit event
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        p.kill()
                        running = False

            # Calculate up/sec
            delta = time.time() - last_time
            dps = 1/delta




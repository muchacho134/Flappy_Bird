import random, sys, time, pygame
import cv2 as cv, mediapipe as mp
from collections import deque as dq
##Initialize##
mp_face_mesh = mp.solutions.face_mesh
mp_dr = mp.solutions.drawing_utils
mp_dr_styles = mp.solutions.drawing_styles
dr_spec = mp_dr.DrawingSpec(thickness = 1, circle_radius = 1)
pygame.init()

VID_CAP = cv.VideoCapture(0)
w_size = (VID_CAP.get(cv.CAP_PROP_FRAME_WIDTH), VID_CAP.get(cv.CAP_PROP_FRAME_HEIGHT)) 
screen = pygame.display.set_mode((w_size))

##Import images##
bird_image = pygame.image.load('bird_sprite.png')
bird_image = pygame.transform.scale(bird_image, (bird_image.get_width() / 8, bird_image.get_height()/8))
bird_frame = bird_image.get_rect()
bird_frame.center = (w_size[0] //8, w_size[1] // 2)

column_frame = dq()
column_image = pygame.image.load('pipe_sprite_single.png')
column_image = pygame.transform.scale(column_image, (column_image.get_width() / 1.3, column_image.get_height()))


column_example = column_image.get_rect()
gap = 120

##Game##
game_time = time.time()
stage = 1
colum_spwn = 0
column_freq = 40
width = 500
column_speed = lambda: width / column_freq
level = 0
score = 0
didUpdateScore = False
game_is_running = True

with mp_face_mesh.FaceMesh(
        max_num_faces = 1,
        refine_landmarks = True,
        min_detection_confidence = 0.5,
        min_tracking_confidence = 0.5) as face_mesh:
    while True:
        if not game_is_running:
            text = pygame.font.SysFont("Helvetica Bold.ttf", 64).render("Game Over!", True, (99, 245, 255))
            tr = text.get_rect()
            tr.center = (w_size[0]/2, w_size[1]/2)
            screen.blit(text, tr)
            pygame.display.update()
            pygame.time.wait(2000)
            VID_CAP.realease()
            cv.destroyAllWindows()
            pygame.quit()
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                VID_CAP.release()
                cv.destroyAllWindows()
                pygame.quit()
                sys.exit()
        ret, frame = VID_CAP.read()
        if not ret:
            print("Empty frame, continuing...")
            continue
        screen.fill((125, 220, 232))

        frame.flags.writeable = False
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = face_mesh.process(frame)
        frame.flags.writeable = True

        if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0:
            marker = results.multi_face_landmarks[0].landmark[94].y
            bird_frame.centery = (marker - 0.5) * 1.5 * w_size[1] +w_size[1]/2
            if bird_frame.top < 0: bird_frame.y = 0
            if bird_frame.bottom > w_size[1]: bird_frame.y = w_size[1] - bird_frame.height

        frame = cv.flip(frame, 1).swapaxes(0, 1)

        for pf in column_frame:
            pf[0].x -= column_speed()
            pf[1].x -= column_speed()
        
        if len(column_frame) > 0 and column_frame[0][0].right < 0:
            column_frame.popleft()

        pygame.surfarray.blit_array(screen,frame)
        screen.blit(bird_image, bird_frame)
        checker = True
        for pf in column_frame:
            if pf[0].left <= bird_frame.x <= pf[0].right:
                checker = False
                if not didUpdateScore:
                    score += 1
                    didUpdateScore = True

            screen.blit(column_image, pf[1])
            screen.blit(pygame.transform.flip(column_image, 0, 1), pf[0])
        if checker: didUpdateScore = False

        #Displaying stage and score
        text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Stage {stage}', True, (99, 245, 255))
        tr = text.get_rect()
        tr.center = (100, 50)
        screen.blit(text, tr)
        text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Score: {score}', True, (99, 245, 255))
        tr = text.get_rect()
        tr.center = (100, 100)
        screen.blit(text, tr)

        pygame.display.flip()  


        if any([bird_frame.colliderect(pf[0]) or bird_frame.colliderect(pf[1])for pf in column_frame]):
            game_is_running = False


        if colum_spwn == 0:
            top = column_example.copy()
            top.x, top.y = w_size[0], int(random.uniform(120 - 1000, w_size[1] - 120 - gap - 1000))
            bottom = column_example.copy()
            bottom.x, bottom.y = w_size[0], top.y + 1000 + gap
            column_frame.append([top, bottom])

        colum_spwn += 1
        if colum_spwn >= column_freq: colum_spwn = 0


        # Update stage

        if time.time() - game_time >= 10:
            column_freq *= 5/6
            stage += 1
            game_time = time.time()


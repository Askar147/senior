import model_call as m

recognizer = m.EmotionRecognizer('.\\first_model.h5')
a = recognizer('C:\\Users\\Admin\\Desktop\\StarWars3.wav')
print(a)


# if os.path.exists(new_file_path) and os.path.isfile(new_file_path):
#     print(f'File created at {new_file_path}')
#     return {f'File created at {new_file_path}'}
# else:
#     print('File not created')
#     return {'not created'}


# fullpath = os.path.join(DESTINATION, file.filename)
# await chunked_copy(file, fullpath)

# DESTINATION = "C:\\Users\\Admin\\Desktop\\fastapi"
# CHUNK_SIZE = 2 ** 20


# async def chunked_copy(src, dst):
#     await src.seek(0)
#     with open(dst, "wb") as buffer:
#         while True:
#             contents = await src.read(CHUNK_SIZE)
#             if not contents:
#                 print(f"Src completely consumed\n")
#                 break
#             print(f"Consumed {len(contents)} bytes from Src file\n")
#             buffer.write(contents)

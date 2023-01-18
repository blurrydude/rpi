
import struct

def create_pbm(pixels, file_name):
  # Open a new file in write mode
  with open(file_name, 'wb') as f:
    # Write the PBM file header
    f.write(b'P4\n')
    # Write the dimensions of the image
    f.write(f'{len(pixels[0])} {len(pixels)}\n'.encode())
    # Iterate over the pixels and write them to the file
    for row in pixels:
      # Pack the pixel values into a byte string
      data = struct.pack('B' * len(row), *row)
      # Write the byte string to the file
      f.write(data)
# Example usage
frames =[
    [
        [0,1,1,1,0],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,0,1,1],
        [1,1,1,1,1],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,1,1,1,0],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,0,1,1],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,0,1,1],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [1,1,0,1,1],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,1,1,1,0]
    ],
    [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0]
    ]
]
i = 0
for frame in frames:
    create_pbm(frame, 'C:\\Code\\rpi\PICO\\frame'+str(i)+'.pbm')
    i = i + 1

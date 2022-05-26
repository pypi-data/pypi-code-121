# Copyright 2020 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import argparse
import tw

if __name__ == "__main__":

  choices = [
      'video_to_img',
      'image_to_video',
      'image_concat',
      'image_concat_vertical',
      'video_concat',
      'video_concat_vertical',
      'resize'
  ]

  parser = argparse.ArgumentParser()
  parser.add_argument('--task', type=str, choices=choices)
  parser.add_argument('--src', type=str, default=None)
  parser.add_argument('--dst', type=str, default=None)
  args, _ = parser.parse_known_args()

  if args.task == 'video_to_img':
    tw.media.video_to_image(args.src)

  elif args.task == 'image_to_video':
    tw.media.image_to_video(args.src, args.dst)

  elif args.task == 'image_concat':
    pass

  elif args.task == 'image_concat_vertical':
    pass

  elif args.task == 'video_concat':
    pass

  elif args.task == 'video_concat_vertical':
    pass

  elif args.task == 'resize':
    pass

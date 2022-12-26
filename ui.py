import sys

class UI:
    def __init__(self, handler, file = "project.mp4"):
        self.handler = handler
        self._start(file)

    def _nums_to_segments(self, nums):
        nums = [num for num in nums if num.isdigit()]
        nums = [num for num in nums if int(num) < len(self.handler.segments)]
        return [self.handler.segments[int(i)] for i in nums]

    def _input_to_command(self, inp):
        if len(inp) <= 0: return False, []
        is_first_letter = not inp[0].isdigit()
        command = "r" if not is_first_letter else inp[0]
        selected = self._nums_to_segments(inp[1:].split()) if is_first_letter else self._nums_to_segments(inp.split())
        return command, selected

    def _print_segments(segments):
        for segment in segments:
            print(f"{segment['id']}: {segment['start']} -> {segment['end']}")
            print(segment['text'])
            print("---" * 25)

    def _edit_segments(segments):
        for segment in segments:
            segment['text'] = editor.edit(contents=segment['text'].encode("UTF-8")).decode("UTF-8")
        return segments

    def _main_loop(self, handler):
        command, selected = self._input_to_command(input("(lazyshorts-py) "))
        if command == "q": # quit
            run = False
        elif command == "p": # print
            self._print_segments(selected if len(selected) > 0 else self.handler.segments)
        elif command == "e": # edit
            if len(selected) > 0:
                UI._print_segments(UI._edit_segments(selected))
            else:
                print("You need to give atleast one segment to edit!")
        elif command == "r": # render
            if len(selected) > 0:
                file = self.handler.render_file(selected, "short.mp4")
                UI._print_segments(selected)
                print(f"Done, wrote to {file}!")
                return file
            else:
                print("You need to give atleast one segment to render!")
        elif not command:
            print("Your input cannot be empty!")
        else:
            print("Sorry, unknown command!")
        return False

    def _handle_preprocess(self, original_file):
        try:
            self.handler.original_video_file = original_file
        except KeyboardInterrupt:
            print("\nUser interrupted video preprocess/transcribe!")
            sys.exit(125)
    def _handle_loop(self):
        run = True
        while run:
            try:
                file = self._main_loop(self.handler)
            except KeyboardInterrupt:
                print()
                sys.exit(0)

    def _start(self, file):
        self._handle_preprocess(file)
        UI._print_segments(self.handler.segments)
        self._handle_loop()

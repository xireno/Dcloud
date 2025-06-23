import sys


def print_progress_bar(iteration, total, prefix="", suffix="", length=50, fill="█"):
    """
    Call in a loop to create a terminal progress bar
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()

def display_progress(iteration, total):
    print_progress_bar(iteration, total, prefix="Progress", suffix="Complete", length=50)

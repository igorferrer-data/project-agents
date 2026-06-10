import os

def count_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count

if __name__ == '__main__':
    print(count_files('/home/iferrer/project-agents'))
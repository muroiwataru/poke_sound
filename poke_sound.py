import pretty_midi

# ノート番号をオクターブと音名に分解
def note_transform(note):
    octave = note // 12 - 1
    sound_name = note % 12

    return octave, format(sound_name, 'X')

# ゲートタイムを対応した数字に変換
# 呼び出し元で返り値を16進数にフォーマットすること [16分音符:0, 8分音符:1, 4分音符:3, 2分音符:7, 全音符:F]
def time_transform(gate_time, tpqn):
    note_value = round(gate_time / (tpqn / 4) - 1)

    if 0 <= note_value:
        return note_value
    else:
        return 'ERROR'

################ パラメータ ################

# 読み込むmidiファイルのパス
midi_file = './midi/hoge.mid'
# 読み込むトラック
track_no = 1
# 分解能, midiファイルによって調整する
tpqn = 240
# 最初の音符（Note）の開始位置
prev_end = 1920

default_octave = 5        # 数字を小さくすると高くなる, 標準:5
volume         = 'D'      # 音量
elapsed_time   = '2 '     # 音が消えるまでの経過時間
speed          = '00 A0 ' # 再生速度

debug = 2   # 音符（Note）の情報を出力するか, 0:しない 1:全て 2:最初の音符のみ

###########################################

# 初期化
output = ''
current_octave = -1

# MIDIファイルのロード
midi_data = pretty_midi.PrettyMIDI(midi_file)
# トラック別で取得
midi_tracks = midi_data.instruments
# トラック[track_no] の音符（Note）を取得
notes = midi_tracks[track_no].notes

for note in notes:

    # 音符（Note）の開始,終了時刻をtick値で取得
    start = midi_data.time_to_tick(note.start)
    end   = midi_data.time_to_tick(note.end)

    # 休符の追加
    # 全音符より長い休符は分割して処理する
    if start > prev_end:
        rest_time = time_transform(start - prev_end, tpqn)
        while rest_time > 15:
            output += 'CF '
            rest_time -= 16

        output += 'C' + format(rest_time,"X") + ' '

    # オクターブと音名の情報を取得
    octave, sound_name = note_transform(note.pitch)

    # オクターブの変更
    if current_octave < octave:
        output += 'E' + format(default_octave - (octave - 5), 'X') + ' '
        current_octave = octave

    elif current_octave > octave:
        output += 'E' + format(default_octave + (5 - octave), 'X') + ' '
        current_octave = octave

    # 音符の追加
    gate_time  = end - start
    note_value = time_transform(gate_time, tpqn)
    # 全音符より長い音符は全音符と休符に置き換える
    while note_value > 15:
        output += sound_name + 'F '
        note_value -= 16
        sound_name = 'C'

    output += sound_name + format(note_value,"X") + ' '

    # 休符を追加するか判定するために音符（Note）の終了時刻を退避
    prev_end = end

    # 音符（Note）の詳細出力
    if debug:
        print(note)
        print('tick:' + str(start) + ' gate_time:' + str(gate_time) + ' octave:' + str(octave) + ' sound_name:' + str(sound_name) + ' note_value:' + str(note_value))
        if debug == 2:
            debug = 0

print('ED ' + speed + 'DC ' + volume + elapsed_time + output + 'FF')
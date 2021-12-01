import json
import argparse
import os
import glob
import capture

staff_agent_list = [
    ('baselineTeam', 'baselineTeam.py'),
]
staff_agent_list += [
    (os.path.basename(p).replace('.py', ''), p)
    for p in sorted(glob.glob('solutions/*.py'))
]

layouts = [
    'defaultCapture',
    'fastCapture',
    'alleyCapture',
    'mediumCapture',
    'distantCapture',
    'strategicCapture',
]
NUM_GAMES = 3  # The number of repeated games to play on each layout


def main(student_agent):
    results = {}
    leaderboard = []
    output_str = ''

    final_score = 0.
    final_num_won = 0
    final_num_played = 0
    for staff_agent_name, staff_agent in staff_agent_list:
        score = 0.
        num_won = 0
        num_played = 0
        repeated_layouts = [(l, n) for l in layouts for n in range(NUM_GAMES)]
        for layout, n_game in repeated_layouts:
            if n_game == 0:
                print('##########################################################')  # NoQA
            print('Playing against {} on {} - game {} / {}.'.format(
                staff_agent_name, layout, n_game+1, NUM_GAMES))

            # Run the pacman game and get its score
            pacman_cmd = 'python capture.py -r {} -b {} -l {} -c -q'
            pacman_cmd_args = pacman_cmd.format(
                student_agent, staff_agent, layout)
            # skip 'python capture.py' in the command line arguments above
            args = capture.readCommand(pacman_cmd_args.split()[2:])
            games = capture.runGames(**args)
            # Take the average of the game scores. Note that there should be
            # only one game in games, unless `-n` is used in pacman.py
            scores = [game.state.data.score for game in games]
            game_score = sum(scores) / len(scores)
            is_victory = (game_score > 0)

            results[(staff_agent_name, layout)] = {
                'game_score': game_score, 'is_victory': is_victory}
            # averaging the scores w.r.t. repeated games
            score += (game_score / NUM_GAMES)
            num_won += int(is_victory)
            num_played += 1

            # Display results
            print('\n\nResult: myTeam (red) vs. {} (blue) on {}:\n'.format(
                staff_agent_name, layout))
            if game_score > 0:
                print('myTeam wins!')
            elif game_score < 0:
                print('{} (your opponent) wins!'.format(staff_agent_name))
            else:
                print('Tie between myTeam and {}!'.format(staff_agent_name))
            print('game score:', game_score)
            if n_game == NUM_GAMES - 1:
                print('##########################################################')  # NoQA

        final_score += score
        final_num_won += num_won
        final_num_played += num_played
        win_rate = num_won / num_played
        leaderboard.append({
            'name': 'Score vs. %s' % staff_agent_name,
            'value': score})
        leaderboard.append({
            'name': 'Winning Rate vs. %s' % staff_agent_name,
            'value': win_rate})
        output_str += 'myTeam vs. %s: Score: %f, Winning Rate: %.3f\n' % (
            staff_agent_name, score, win_rate)

    final_win_rate = final_num_won / final_num_played
    leaderboard.append({
        'name': 'Final Score',
        'value': final_score})
    leaderboard.append({
        'name': 'Final Winning Rate',
        'value': final_win_rate})
    output_str += 'Final results: Score: %f, Winning Rate: %.3f\n' % (
        final_score, final_win_rate)
    output_str += '\nDetails shown below:\n'

    # Generate results.json
    score_fields = {}
    score_fields['score'] = final_score
    score_fields['leaderboard'] = leaderboard
    score_fields['output'] = output_str
    write_output(score_fields)


def write_output(score_fields):
    with open('results.json', 'w') as output_file:
        json.dump(score_fields, output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pacman', default='myTeam.py')
    args = parser.parse_args()
    main(args.pacman)

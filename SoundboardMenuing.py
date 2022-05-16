from typing import Optional

from Group import Group
from Menu import Menu
from Option import Option
from Strike import strike


def is_not_int(min_range: Optional[int], max_range: Optional[int], test: str):
    try:
        test_int = int(test)
    except ValueError:
        return True
    if min_range is not None and min_range > test_int:
        return True
    if max_range is not None and max_range < test_int:
        return True
    return False


def group_chooser_action(group_chooser: Menu, group_list: list[Group], user_choice: str):
    if int(user_choice)-2 == len(group_chooser.children):
        group_chooser.parent.show_to_user()
    elif int(user_choice)-1 == len(group_chooser.children):
        group_chooser.tempCondense = not group_chooser.tempCondense
        group_chooser.prompt = make_group_list_prompt(group_list, group_chooser.tempCondense)
        group_chooser.show_to_user()
    elif int(user_choice)-1 < len(group_chooser.children):
        group_chooser.children[int(user_choice) - 1].show_to_user()


def make_group_list_prompt(group_list: list[Group], condensed: bool):
    sounds_editor_prompt = "-----\n"
    number_of_groups = len(group_list)
    for i in range(number_of_groups):
        if condensed:
            sounds_editor_prompt += str(i + 1) + ". " + group_list[i].name + "\n"
            continue
        sounds_editor_prompt += str(i+1) + ". " + group_list[i].name + " - " + group_list[i].hotkeys[0]
        for j in range(1, len(group_list[i].hotkeys)):
            sounds_editor_prompt += " | " + group_list[i].hotkeys[j]
        sounds_editor_prompt += "\n"
        play_style = "Plays Randomly"
        if not group_list[i].playRandomly:
            play_style = strike(play_style)
        sounds_editor_prompt += "\t  " + play_style
        for j in range(len(group_list[i].groupEntries)):
            sounds_editor_prompt += "\n\t" + group_list[i].groupEntries[j].soundEntry.filePath[7:-4]
            if group_list[i].playRandomly:
                sounds_editor_prompt += " - " + str(group_list[i].groupEntries[j].weight)
        sounds_editor_prompt += "\n"
    sounds_editor_prompt += str(number_of_groups+1)
    if condensed:
        sounds_editor_prompt += ". Un-condense Sound Groups\n"
    else:
        sounds_editor_prompt += ". Condense Sound Groups\n"
    sounds_editor_prompt += str(number_of_groups+2) + ". Back\nYour choice: "
    return sounds_editor_prompt


def make_group_chooser_menus(group_chooser: Menu, group_list: list[Group]):
    for group in group_list:
        group_chooser.add_child(make_group_prompt(group), is_not_int, (1, 4))


def make_group_prompt(group: Group):
    group_prompt = "-----\n"
    group_prompt += group.name + " - " + group.hotkeys[0]
    for j in range(1, len(group.hotkeys)):
        group_prompt += " | " + group.hotkeys[j]
    group_prompt += "\n"
    play_style = "Plays Randomly"
    if not group.playRandomly:
        play_style = strike(play_style)
    group_prompt += "\t  " + play_style
    number_of_entries = len(group.groupEntries)
    for j in range(number_of_entries):
        group_prompt += "\n" + str(j+1) + ". " + group.groupEntries[j].soundEntry.filePath[7:-4]
        if group.playRandomly:
            group_prompt += " - " + str(group.groupEntries[j].weight)
    group_prompt += str(number_of_entries+1) + ". Change Group Name\n" + str(number_of_entries+2) + \
        ". Change Hotkeys\n" + str(number_of_entries+3) + ". Change Play Style\n" + str(number_of_entries+4) + ". Back"
    return group_prompt

def make_group_action(group: Menu, user_choice: str):
    if int(user_choice) - 1 == len(group.children) and group.parent is not None:
        group.parent.show_to_user()
    elif int(user_choice) - 1 < len(self.children):
        self.children[int(user_choice) - 1].show_to_user()


def soundboard_menu(group_list: list[Group], options: dict[str, Option]):
    main_prompt = "-----\nWhat would you like to do?\n\t1. Change Sounds\n\t2. Change Settings\n" \
                  "\t3. Save and Restart\n\t4. Cancel Pending Changes\n\t5. Quit\nYour choice: "
    main = Menu(main_prompt, is_not_int, (1, 5))
    group_chooser = main.add_child(make_group_list_prompt(group_list, options["Condense Sound Group Editor"].state),
                                   is_not_int,
                                   (1, len(group_list) + 2),
                                   group_chooser_action)
    group_chooser.actionArgs = (group_chooser, group_list)  # Might be shady
    group_chooser.tempCondense = options["Condense Sound Group Editor"].state  # This is a little sus
    make_group_chooser_menus(group_chooser, group_list)
    main.show_to_user()


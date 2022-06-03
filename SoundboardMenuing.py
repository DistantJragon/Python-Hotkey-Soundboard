from typing import Optional

from Group import Group
from GroupEntry import GroupEntry
from MenuICPG import MenuICPG
from Soundboard import Soundboard
from TextFormatting import grey_out, brighten, enable_formatting
from MenuIC import is_not_int_in_range, MenuIC


def group_chooser_action(group_chooser: MenuICPG, user_choice: str, group_list: list[Group]):
    if int(user_choice) <= len(group_list):
        entry_chooser = group_chooser.children[0]
        chosen_group = group_list[int(user_choice) - 1]
        entry_chooser.promptArgs = (chosen_group,)
        entry_chooser.checkArgs = (1, len(chosen_group.groupEntries) + 5)
        entry_chooser.actionArgs = (chosen_group,)
        entry_chooser.show_to_user()
    elif int(user_choice) == len(group_list) + 1:
        group_chooser.promptArgs = (group_list, not group_chooser.promptArgs[1])
        group_chooser.show_to_user()
    elif int(user_choice) == len(group_list) + 2:
        group_chooser.parent.show_to_user()


def make_group_chooser_prompt(group_list: list[Group], condensed: bool):
    group_chooser_prompt = "-----\n"
    number_of_groups = len(group_list)
    for i in range(number_of_groups):
        if condensed:
            group_chooser_prompt += str(i + 1) + ". " + group_list[i].name + "\n"
            continue
        group_chooser_prompt += str(i + 1) + ". " + group_list[i].name + " - " + group_list[i].hotkeys[0]
        for j in range(1, len(group_list[i].hotkeys)):
            group_chooser_prompt += " | " + group_list[i].hotkeys[j]
        group_chooser_prompt += "\n"
        play_style = "Plays Randomly"
        if group_list[i].playRandomly:
            play_style = brighten(play_style)
        else:
            play_style = grey_out(play_style)

        group_chooser_prompt += "\t  " + play_style
        for j in range(len(group_list[i].groupEntries)):
            group_chooser_prompt += "\n\t" + group_list[i].groupEntries[j].soundEntry.filePath[7:-4]
            if group_list[i].playRandomly:
                group_chooser_prompt += " - " + str(group_list[i].groupEntries[j].weight)
        group_chooser_prompt += "\n"
    group_chooser_prompt += str(number_of_groups + 1)
    if condensed:
        group_chooser_prompt += ". Un-condense Sound Groups\n"
    else:
        group_chooser_prompt += ". Condense Sound Groups\n"
    group_chooser_prompt += str(number_of_groups + 2) + ". Back\nYour choice: "
    return group_chooser_prompt


def entry_chooser_action(entry_chooser: MenuICPG, user_choice: str, group: Group, ):
    if int(user_choice) <= len(group.groupEntries):
        entry_chooser.children[0].show_to_user()
    elif int(user_choice) == len(group.groupEntries) + 5:
        entry_chooser.parent.show_to_user()
    elif int(user_choice) == len(group.groupEntries) + 4 and group.playRandomly:
        entry_chooser.show_to_user()
    elif int(user_choice) <= len(group.groupEntries) + 5:
        entry_chooser.children[int(user_choice) - len(entry_chooser.children)].show_to_user()


def make_entry_chooser_prompt(group: Group):
    group_prompt = "-----\n"
    group_prompt += group.name + " - " + group.hotkeys[0]
    for j in range(1, len(group.hotkeys)):
        group_prompt += " | " + group.hotkeys[j]
    group_prompt += "\n"
    play_style = "Plays Randomly"
    if group.playRandomly:
        play_style = brighten(play_style)
    else:
        play_style = grey_out(play_style)
    group_prompt += "\t  " + play_style
    number_of_entries = len(group.groupEntries)
    for j in range(number_of_entries):
        group_prompt += "\n" + str(j + 1) + ". " + group.groupEntries[j].soundEntry.filePath[7:-4]
        if group.playRandomly:
            group_prompt += " - " + str(group.groupEntries[j].weight)
    group_prompt += "\n\t" + str(number_of_entries + 1) + ". Change Group Name\n\t" + str(number_of_entries + 2) + \
                    ". Change Hotkeys\n\t" + str(number_of_entries + 3) + ". Change Play Style\n\t"
    reorder = str(number_of_entries + 4) + ". Reorder Sounds"
    if group.playRandomly:
        reorder = grey_out(reorder)
    group_prompt += reorder + "\n\t" + str(number_of_entries + 5)
    group_prompt += ". Back\nYour choice: "
    return group_prompt


def entry_editor_action(entry_editor: MenuICPG, user_choice: str, group: Group, entry: GroupEntry):
    pass


def soundboard_menu(soundboard: Soundboard):
    group_list = soundboard.groupList
    options = soundboard.options
    main_prompt = "-----\nWhat would you like to do?\n1. Change Sounds\n2. Change Settings\n" \
                  "3. Save and Restart\n4. Cancel Pending Changes\n5. Quit\nYour choice: "
    main = MenuIC(is_not_int_in_range, (1, 5), prompt=main_prompt)
    group_chooser = MenuICPG(is_not_int_in_range,
                             (1, len(group_list) + 2),
                             prompt_getter=make_group_chooser_prompt,
                             prompt_args=(group_list, options["Condense Sound Group Editor"].state),
                             action=group_chooser_action,
                             action_args=(group_list,))
    main.add_child(group_chooser)
    entry_chooser = MenuICPG(is_not_int_in_range, (), prompt_getter=make_entry_chooser_prompt,
                             action=entry_chooser_action)
    group_chooser.add_child(entry_chooser)
    entry_editor = MenuIC()
    entry_chooser.add_child(entry_editor)
    enable_formatting()
    main.show_to_user()

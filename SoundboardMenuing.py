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


def group_chooser_action(group_chooser: Menu, user_choice: str, group_list: list[Group]):
    if int(user_choice) <= len(group_list):
        group_chooser.children[0].promptArgs = (group_list[int(user_choice) - 1],)
        group_chooser.children[0].checkArgs = (1, len(group_list) + 5)
        group_chooser.children[0].actionArgs = (group_list[int(user_choice) - 1],)
        group_chooser.children[0].show_to_user()
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
        group_chooser_prompt += str(i+1) + ". " + group_list[i].name + " - " + group_list[i].hotkeys[0]
        for j in range(1, len(group_list[i].hotkeys)):
            group_chooser_prompt += " | " + group_list[i].hotkeys[j]
        group_chooser_prompt += "\n"
        play_style = "Plays Randomly"
        if not group_list[i].playRandomly:
            play_style = strike(play_style)
        group_chooser_prompt += "\t  " + play_style
        for j in range(len(group_list[i].groupEntries)):
            group_chooser_prompt += "\n\t" + group_list[i].groupEntries[j].soundEntry.filePath[7:-4]
            if group_list[i].playRandomly:
                group_chooser_prompt += " - " + str(group_list[i].groupEntries[j].weight)
        group_chooser_prompt += "\n"
    group_chooser_prompt += str(number_of_groups+1)
    if condensed:
        group_chooser_prompt += ". Un-condense Sound Groups\n"
    else:
        group_chooser_prompt += ". Condense Sound Groups\n"
    group_chooser_prompt += str(number_of_groups+2) + ". Back\nYour choice: "
    return group_chooser_prompt


def entry_chooser_action(entry_chooser: Menu, user_choice: str, group: Group, ):
    if int(user_choice) <= len(group.groupEntries):
        entry_chooser.children[0].show_to_user()
    elif int(user_choice) == len(group.groupEntries) + 5:
        entry_chooser.parent.show_to_user()
    else:
        entry_chooser.children[int(user_choice) - len(entry_chooser.children) - 1].show_to_user()


def make_entry_chooser_prompt(group: Group):
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
    group_prompt += "\n\t" + str(number_of_entries+1) + ". Change Group Name\n\t" + str(number_of_entries+2) + \
                    ". Change Hotkeys\n\t" + str(number_of_entries+3) + ". Change Play Style\n\t" + \
                    str(number_of_entries+4) + ". Reorder Sounds\n\t" + str(number_of_entries+5) + \
                    ". Back\nYour choice: "
    return group_prompt


def entry_editor_action():
    pass


def soundboard_menu(group_list: list[Group], options: dict[str, Option]):
    main_prompt = "-----\nWhat would you like to do?\n\t1. Change Sounds\n\t2. Change Settings\n" \
                  "\t3. Save and Restart\n\t4. Cancel Pending Changes\n\t5. Quit\nYour choice: "
    main = Menu(is_not_int, (1, 5), prompt=main_prompt)
    group_chooser = main.add_child(is_not_int,
                                   (1, len(group_list) + 2),
                                   prompt_getter=make_group_chooser_prompt,
                                   prompt_args=(group_list, options["Condense Sound Group Editor"].state),
                                   action=group_chooser_action,
                                   action_args=(group_list,))
    entry_chooser = group_chooser.add_child(is_not_int, (),
                                            prompt_getter=make_entry_chooser_prompt,
                                            action=entry_chooser_action)
    entry_editor = entry_chooser.add_child(is_not_int, ())
    # for group in group_list:
    #     group_menu = group_chooser.add_child(make_group_prompt(group), is_not_int, (1, 4), group_action)
    #     group_menu.actionArgs = (group_menu,)
    main.show_to_user()

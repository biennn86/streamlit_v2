# import streamlit as st

# #st.experimental_dialog
# @st.experimental_dialog("Cast your vote")
# def vote(item):
#     st.write(f"Why is {item} your favorite?")
#     reason = st.text_input("Because...")
#     if st.button("Submit"):
#         st.session_state.vote = {"item": item, "reason": reason}
#         print(st.session_state)
#         st.rerun()

# if "vote" not in st.session_state:
#     st.write("Vote for your favorite")
#     if st.button("A"):
#         vote("A")
#     if st.button("B"):
#         vote("B")
# else:
#     f"You voted for {st.session_state.vote['item']} because {st.session_state.vote['reason']}"

#=================================
#st.container
# import streamlit as st

# row1 = st.columns(3)
# row2 = st.columns(3)
# print(row1 + row2)

# for col in row1 + row2:
#     tile = col.container(height=120)
#     tile.title(":balloon:")
import json
def load_contacts():
    try:
        with open("contacts.json","r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_contacts(contacts):
    with open("contacts.json","w") as file:
        json.dump(contacts,file,indent=4)

def add_contact(contacts):
    name=input("enter name")
    phone=input("enter phone")
    email=input("enter email")
    contact={
        "name":name,
        "phone":phone,
        "email":email
    }
    contacts.append(contact)
    save_contacts(contacts)
    print("contact added successfully")

def view_contacts(contacts):
    if not contacts:
        print("no contacts found")
        return
    print("\ncontacts")
    for contact in contacts:
        print("\nName :", contact["name"])
        print("Phone:", contact["phone"])
        print("Email:", contact["email"])

def search_contact(contacts):
    name=input("enter name")
    for contact in contacts:
        if contact["name"].lower()==name.lower():
            print("contact found in contacts")
            print("\nName :", contact["name"])
            print("Phone:", contact["phone"])
            print("Email:", contact["email"])
            return
    print("contact not found in contacts") 

def update_contact(contacts):
    name=input("enter name")
    for contact in contacts:
        if contact["name"].lower()==name.lower():
            contact["phone"] = input("Enter new phone")
            contact["email"] = input("Enter new email")
            save_contacts(contacts)
            print("contacts saved")
            return
    print("contact not found in contacts")

def delete_contact(contacts):
    name=input("enter name to be deleted")
    for contact in contacts:
        if contact["name"].lower()==name.lower():
            contacts.remove(contact)
            save_contacts(contacts)
            print("contact deleted")
            return 
    print("contact not found in contacts")

def main():
    contacts = load_contacts()

    while True:
        print("\n===== CONTACT BOOK =====")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Search Contact")
        print("4. Update Contact")
        print("5. Delete Contact")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_contact(contacts)

        elif choice == "2":
            view_contacts(contacts)

        elif choice == "3":
            search_contact(contacts)

        elif choice == "4":
            update_contact(contacts)

        elif choice == "5":
            delete_contact(contacts)

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice!")
main()

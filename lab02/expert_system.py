import json
import sys


def load_expert_system(filepath):
  try:
    with open(filepath, "r", encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku {filepath}")
    sys.exit(1)
  except json.JSONDecodeError:
    print("Błąd: Nie poprawny format JSON w pliku.")
    sys.exit(1)


def ask_questions(questions_data):
  user_answers = {}
  print("--- SYSTEM EKSPERCKI: DIAGNOSTYKA LINUX ---")
  print(
      "Odpowiadaj na pytania, wpisując dokładnie jedną z dostępnych opcji.\n"
  )

  for q_id, q_info in questions_data.items():
    print(f"\n[{q_id}] {q_info['text']}")
    print(f"Dostępne opcje: {', '.join(q_info['answers'])}")

    while True:
      ans = input("Twoja odpowiedź: ").strip()
      if ans in q_info["answers"]:
        user_answers[q_id] = ans
        break
      else:
        print(
            "Nieprawidłowa odpowiedź. Wybierz jedną z opcji:"
            f" {q_info['answers']}"
        )

  return user_answers


def evaluate_rules(rules, user_answers):
  matched_rules = []

  for rule in rules:
    condition_met = True
    for q_id, required_value in rule["if"].items():
      if user_answers.get(q_id) != required_value:
        condition_met = False
        break

    if condition_met:
      matched_rules.append(rule)

  return matched_rules


def main():
  json_filepath = "expert_system.json"

  data = load_expert_system(json_filepath)

  user_answers = ask_questions(data["questions"])

  matched_rules = evaluate_rules(data["rules"], user_answers)

  print("\n" + "=" * 50)
  print("WYNIKI DIAGNOZY I ZALECENIA:")
  print("=" * 50)

  if matched_rules:
    for idx, rule in enumerate(matched_rules, 1):
      print(f"\nReguła #{idx}:")
      print(f"  • Diagnoza: {rule['then']['diagnosis']}")
      print(f"  • Działanie: {rule['then']['action']}")
  else:
    print(
        "\nNie znaleziono pasujących reguł dla podanych odpowiedzi w bazie"
    )


if __name__ == "__main__":
  main()

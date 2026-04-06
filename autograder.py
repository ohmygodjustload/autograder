import os
import requests
import time
import html
import re

CANVAS_DOMAIN = "https://uwlac.instructure.com"

ACCESS_TOKEN = os.environ["CANVAS_TOKEN"]

COURSE_ID = 831226
ASSIGNMENT_ID = 9754940

WORD_COUNT_MIN = 100
SCORE_TO_GIVE = 1

base_url = f"{CANVAS_DOMAIN}/api/v1"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

DRY_RUN = True

def get_submissions(course_id, assignment_id):
    url = f"{base_url}/courses/{course_id}/assignments/{assignment_id}/submissions"
    params = {"per_page": 100, "include": ["user"]}
    all_submissions = []

    while url:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        params = None
        if response.status_code != 200:
            print(f"Error fetching submissions: {response.status_code} - {response.text}")
            return None

        submissions = response.json()
        if not submissions:
            break

        all_submissions.extend(submissions)
        print(f"Fetched {len(submissions)} submissions (total so far: {len(all_submissions)})")

        # Move to next page if available
        url = response.links.get("next", {}).get("url")

    return all_submissions

def count_words(text):
    if not text:
        return 0
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'https?://\S+', '', text)
    words = text.split()
    words = [w for w in words if re.search(r'\w', w)]
    return len(words)

def grade_submission(submission, assignment_id):
    if DRY_RUN:
        print(f"[DRY RUN] Would grade {submission.get('user',{}).get('name','Unknown')} with {SCORE_TO_GIVE} points")
        return True
    else:
        url = f"{base_url}/courses/{submission['course_id']}/assignments/{assignment_id}/submissions/{submission['user_id']}"
        grade_data = {"submission": {"posted_grade": str(SCORE_TO_GIVE)}}
        response = requests.put(url, headers=headers, json=grade_data, timeout=10)
        if response.status_code in (200, 201):
            return True
        else:
            print(f"Error grading user {submission['user_id']}: {response.status_code} - {response.text}")
            return False

def main():
    print("Starting autograder...")
    print(f"Course ID: {COURSE_ID}, Assignment ID: {ASSIGNMENT_ID}")

    print("Fetching submissions...")
    submissions = get_submissions(COURSE_ID, ASSIGNMENT_ID)
    if submissions is None:
        print("Failed to fetch submissions. Exiting.")
        return

    print(f"Processing {len(submissions)} submissions...")
    graded_count = 0
    skipped_count = 0

    for sub in submissions:
        user_name = sub.get('user', {}).get('name', 'Unknown')
        user_id = sub['user_id']

        # Skip if already graded
        if sub.get('grade') is not None:
            print(f"Skipping {user_name} (already graded with grade: {sub['grade']})")
            skipped_count += 1
            continue

        submission_text = sub.get('body', '')
        word_count = count_words(submission_text)

        print(f"Grading {user_name} (word count: {word_count})...")

        if word_count >= WORD_COUNT_MIN:
            success = grade_submission(sub, ASSIGNMENT_ID)
            if success:
                print(f"Graded {user_name} with {SCORE_TO_GIVE} points")
                graded_count += 1
            else:
                print(f"Failed to grade {user_name}")
        else:
            print(f"Below word count threshold, skipping {user_name}")
            skipped_count += 1

        time.sleep(0.5)  # avoid rate limits

    # Summary
    print("\nGrading Summary:")
    print(f"Total submissions: {len(submissions)}")
    print(f"Graded: {graded_count}")
    print(f"Skipped: {skipped_count}")

if __name__ == "__main__":
    main()
import requests
import matplotlib.pyplot as plt


USERNAME = "chealyC"
OUTPUT_FILE = "language_graph.svg"


def get_repositories():
    """Return all public repositories belonging to the user."""

    repositories = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?per_page=100&page={page}"
        )

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        page_data = response.json()

        if not page_data:
            break

        repositories.extend(page_data)
        page += 1

    return repositories


def get_repository_languages(repository):
    """Return GitHub's language statistics for a repository."""

    response = requests.get(
        repository["languages_url"],
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def calculate_languages(repositories):
    """Combine language statistics from all repositories."""

    languages = {}

    for repository in repositories:

        # Ignore forks.
        if repository["fork"]:
            continue

        repository_languages = get_repository_languages(repository)

        for language, byte_count in repository_languages.items():
            languages[language] = (
                languages.get(language, 0) + byte_count
            )

    return languages


def calculate_percentages(languages):
    """Convert language byte counts into percentages."""

    total = sum(languages.values())

    if total == 0:
        return {}

    return {
        language: (bytes_used / total) * 100
        for language, bytes_used in languages.items()
    }


def prepare_chart_data(percentages):
    """Keep significant languages and group the rest as Other."""

    sorted_languages = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True
    )

    chart_data = {}
    other_percentage = 0

    for language, percentage in sorted_languages:

        if percentage >= 2:
            chart_data[language] = percentage
        else:
            other_percentage += percentage

    if other_percentage > 0:
        chart_data["Other"] = other_percentage

    return chart_data


def create_graph(chart_data):
    """Create the SVG doughnut chart."""

    plt.figure(figsize=(8, 5.5))

    wedges, _ = plt.pie(
        chart_data.values(),
        startangle=90,
        wedgeprops={"width": 0.42}
    )

    # Centre text
    plt.text(
        0,
        0,
        "Programming\nLanguages",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold"
    )

    # Legend with percentages
    legend_labels = [
        f"{language} — {percentage:.1f}%"
        for language, percentage in chart_data.items()
    ]

    plt.legend(
        wedges,
        legend_labels,
        title="Languages",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=False
    )

    plt.axis("equal")

    plt.savefig(
        OUTPUT_FILE,
        format="svg",
        bbox_inches="tight",
        transparent=True
    )

    plt.close()


def main():
    print(f"Checking GitHub repositories for {USERNAME}...")

    repositories = get_repositories()

    print(f"Found {len(repositories)} repositories.")

    languages = calculate_languages(repositories)

    if not languages:
        print("No programming languages found.")
        return

    percentages = calculate_percentages(languages)

    chart_data = prepare_chart_data(percentages)

    print("\nLanguage distribution:")

    for language, percentage in chart_data.items():
        print(f"{language}: {percentage:.1f}%")

    create_graph(chart_data)

    print(f"\nGraph created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
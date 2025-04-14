def summarize_text(text, llm, max_tokens=150):
    """
    Summarize the given text using ChatOpenAI.
    The prompt instructs the LLM to provide a concise summary.
    """
    prompt = f"Please summarize the following text in a concise and clear manner:\n\n{text}\n\nSummary:"
    result = llm.invoke(prompt, max_tokens=max_tokens)
    # Access the .content attribute and strip any extra whitespace.
    summary = result.content.strip()
    return summary

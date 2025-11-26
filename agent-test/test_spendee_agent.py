import asyncio
import pytest
import spendee_agent

@pytest.mark.asyncio
async def test_example_usage_with_real_llm():
    """
    Tests that the example_usage function, when making a real LLM call,
    returns a response that contains the expected keyword.
    """
    # Arrange
    question = "Why is the sky blue? Explain in two sentences, mentioning the scientific name for the scattering effect."

    # Act
    #response = await spendee_agent.example_usage(question)
    try:
        response = await asyncio.wait_for(
            spendee_agent.example_usage(question),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        pytest.fail("Test timed out after 30 seconds - likely due to hanging background tasks")


    # Assert
    assert response is not None, "The LLM response should not be None."
    assert "rayleigh" in response.lower(), "The response should contain the word 'Rayleigh'."

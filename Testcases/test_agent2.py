from agents import agent2_deduplication

def test_similarity_identical():
    assert agent2_deduplication._similarity("hello world", "hello world") == 1.0
    assert agent2_deduplication._similarity("hello world", "HELLO WORLD") == 1.0

def test_similarity_different():
    assert agent2_deduplication._similarity("abc", "xyz") == 0.0

def test_similarity_partial():
    # SequenceMatcher of "abc" and "ab" should be 4 / 5 = 0.8
    # Match length: 2 ("ab"). Total chars: 3 + 2 = 5. Ratio: 2 * 2 / 5 = 0.8.
    assert agent2_deduplication._similarity("abc", "ab") == 0.8

def test_deduplication_no_duplicates():
    collected_data = {
        "all_incidents": [
            {"source": "chat", "id": "C1", "title": "Memory leak on production"},
            {"source": "ticket", "id": "T1", "title": "CPU utilization spiked"}
        ]
    }
    result = agent2_deduplication.run(collected_data)
    assert len(result["unique_incidents"]) == 2
    assert result["total_unique"] == 2
    assert result["total_duplicates"] == 0
    assert len(result["duplicates"]) == 0

def test_deduplication_chat_vs_ticket():
    # When similarity >= 0.70, keep ticket over chat
    collected_data = {
        "all_incidents": [
            {"source": "chat", "id": "C1", "title": "Database is running out of memory"},
            {"source": "ticket", "id": "T1", "title": "Database running out of memory"}
        ]
    }
    result = agent2_deduplication.run(collected_data)
    assert len(result["unique_incidents"]) == 1
    assert result["unique_incidents"][0]["source"] == "ticket"
    assert result["unique_incidents"][0]["id"] == "T1"
    assert result["total_duplicates"] == 1
    assert result["duplicates"][0]["removed"] == "Database is running out of memory"
    assert result["duplicates"][0]["kept"] == "Database running out of memory"

def test_deduplication_first_wins():
    # When both are chat/ticket, keep the first one
    collected_data = {
        "all_incidents": [
            {"source": "chat", "id": "C1", "title": "Database is running out of memory"},
            {"source": "chat", "id": "C2", "title": "Database running out of memory"}
        ]
    }
    result = agent2_deduplication.run(collected_data)
    assert len(result["unique_incidents"]) == 1
    assert result["unique_incidents"][0]["id"] == "C1"
    assert result["total_duplicates"] == 1
    assert result["duplicates"][0]["removed"] == "Database running out of memory"
    assert result["duplicates"][0]["kept"] == "Database is running out of memory"

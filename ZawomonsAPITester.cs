using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using TMPro;

public class ZawomonsAPITester : MonoBehaviour
{
    [Header("UI Elements")]
    public TMP_Text playerDataText;
    public TMP_Text saveResultText;
    public TMP_Text playersListText;
    
    [Header("API Settings")]
    public string baseUrl = "http://127.0.0.1:8000/api/v1/games/zawomons";
    
    // Token można pobrać z localStorage poprzez JavaScript interop
    private string authToken = "";
    
    void Start()
    {
        // Pobierz token z przeglądarki (tylko WebGL)
        GetAuthTokenFromBrowser();
    }
    
    // Funkcja do pobierania tokena z localStorage przeglądarki
    void GetAuthTokenFromBrowser()
    {
        #if UNITY_WEBGL && !UNITY_EDITOR
            authToken = GetTokenFromLocalStorage();
            if (string.IsNullOrEmpty(authToken))
            {
                Debug.LogWarning("Brak tokena autoryzacji! Użytkownik nie jest zalogowany.");
                playerDataText.text = "BŁĄD: Użytkownik nie jest zalogowany!";
            }
            else
            {
                Debug.Log("Token pobrany: " + authToken.Substring(0, 10) + "...");
            }
        #else
            // W edytorze używamy testowego tokena (musisz go pobrać z Postmana/przeglądarki)
            authToken = "your_test_token_here";
            Debug.LogWarning("Uruchomione w edytorze - używam testowego tokena");
        #endif
    }
    
    // JavaScript interop dla WebGL - pobieranie z localStorage
    [System.Runtime.InteropServices.DllImport("__Internal")]
    private static extern string GetTokenFromLocalStorage();
    
    // Przycisk 1: Pobierz dane gracza
    public void GetPlayerData()
    {
        StartCoroutine(GetPlayerDataCoroutine());
    }
    
    IEnumerator GetPlayerDataCoroutine()
    {
        string url = baseUrl + "/player-data/";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            // Dodaj header autoryzacji
            if (!string.IsNullOrEmpty(authToken))
            {
                request.SetRequestHeader("Authorization", "Bearer " + authToken);
            }
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                string jsonResponse = request.downloadHandler.text;
                Debug.Log("Player Data Response: " + jsonResponse);
                
                // Parse JSON response
                PlayerDataResponse playerData = JsonUtility.FromJson<PlayerDataResponse>(jsonResponse);
                
                playerDataText.text = $"Gracz: {playerData.username}\n" +
                                     $"Złoto: {playerData.gold}\n" +
                                     $"Drewno: {playerData.wood}\n" +
                                     $"Kamień: {playerData.stone}\n" +
                                     $"Gemy: {playerData.gems}\n" +
                                     $"Creatures: {playerData.creatures.Length}";
            }
            else
            {
                Debug.LogError("Error getting player data: " + request.error);
                playerDataText.text = "BŁĄD: " + request.error + "\n" + request.downloadHandler.text;
            }
        }
    }
    
    // Przycisk 2: Zapisz dane gracza
    public void SavePlayerData()
    {
        StartCoroutine(SavePlayerDataCoroutine());
    }
    
    IEnumerator SavePlayerDataCoroutine()
    {
        string url = baseUrl + "/save-data/";
        
        // Przykładowe dane do zapisu
        var saveData = new
        {
            name = "TestPlayer",
            gold = 500,
            wood = 200,
            stone = 100,
            gems = 25
        };
        
        string jsonData = JsonUtility.ToJson(saveData);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            // Dodaj header autoryzacji
            if (!string.IsNullOrEmpty(authToken))
            {
                request.SetRequestHeader("Authorization", "Bearer " + authToken);
            }
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Save successful: " + request.downloadHandler.text);
                saveResultText.text = "ZAPISANO POMYŚLNIE!\n" + request.downloadHandler.text;
            }
            else
            {
                Debug.LogError("Error saving data: " + request.error);
                saveResultText.text = "BŁĄD ZAPISU: " + request.error + "\n" + request.downloadHandler.text;
            }
        }
    }
    
    // Przycisk 3: Pobierz listę wszystkich graczy
    public void GetPlayersList()
    {
        StartCoroutine(GetPlayersListCoroutine());
    }
    
    IEnumerator GetPlayersListCoroutine()
    {
        string url = baseUrl + "/players/";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            // Dodaj header autoryzacji
            if (!string.IsNullOrEmpty(authToken))
            {
                request.SetRequestHeader("Authorization", "Bearer " + authToken);
            }
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                string jsonResponse = request.downloadHandler.text;
                Debug.Log("Players List Response: " + jsonResponse);
                
                // Parse JSON array
                PlayerListItem[] players = JsonUtility.FromJson<PlayerListWrapper>("{\"players\":" + jsonResponse + "}").players;
                
                string playersText = "LISTA GRACZY:\n";
                foreach (var player in players)
                {
                    playersText += $"• {player.username} ({player.name}) - Złoto: {player.gold}, Creatures: {player.creature_count}\n";
                }
                
                playersListText.text = playersText;
            }
            else
            {
                Debug.LogError("Error getting players list: " + request.error);
                playersListText.text = "BŁĄD: " + request.error + "\n" + request.downloadHandler.text;
            }
        }
    }
}

// Data classes for JSON parsing
[System.Serializable]
public class PlayerDataResponse
{
    public int id;
    public string username;
    public int gold;
    public int wood;
    public int stone;
    public int gems;
    public bool can_claim_start_creature;
    public CreatureData[] creatures;
    public string last_played;
    public string created_at;
}

[System.Serializable]
public class CreatureData
{
    public int id;
    public string name;
    public string main_element;
    public string secondary_element;
    public string color;
    public int experience;
    public int max_hp;
    public int current_hp;
    public int max_energy;
    public int current_energy;
    public int damage;
    public int initiative;
}

[System.Serializable]
public class PlayerListItem
{
    public string username;
    public string name;
    public int gold;
    public int creature_count;
    public string last_played;
}

[System.Serializable]
public class PlayerListWrapper
{
    public PlayerListItem[] players;
}

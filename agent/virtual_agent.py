import re
import unicodedata
from mcp.client import MCPClient
from core.models import CombustivelEnum, TransmissaoEnum

MARCAS_E_MODELOS_PARA_AGENTE = {
    "Fiat": ["Uno", "Palio", "Strada", "Toro", "Argo", "Mobi", "Cronos", "Pulse", "Fastback"],
    "Volkswagen": ["Gol", "Polo", "Virtus", "T-Cross", "Nivus", "Saveiro", "Amarok", "Taos", "Jetta", "Voyage"],
    "Chevrolet": ["Onix", "Prisma", "Tracker", "S10", "Cruze", "Montana", "Spin", "Equinox", "Joy"],
    "Ford": ["Ka", "Fiesta", "EcoSport", "Ranger", "Territory", "Bronco", "Maverick"],
    "Hyundai": ["HB20", "Creta", "Tucson", "Santa Fe", "HB20S", "IX35"],
    "Toyota": ["Corolla", "Hilux", "Yaris", "SW4", "Corolla Cross", "RAV4", "Etios"],
    "Renault": ["Sandero", "Logan", "Duster", "Kwid", "Captur", "Oroch"],
    "Honda": ["Civic", "Fit", "City", "HR-V", "WR-V", "CR-V"],
    "Jeep": ["Renegade", "Compass", "Commander", "Wrangler", "Gladiator"],
    "Nissan": ["Kicks", "Versa", "Frontier", "Sentra", "March"],
    "Peugeot": ["208", "2008", "3008", "Partner", "Boxer"],
    "Citroën": ["C3", "C4 Cactus", "Jumpy", "Jumper"],
    "Mitsubishi": ["L200 Triton", "Pajero Sport", "Eclipse Cross", "Outlander", "ASX"],
    "BMW": ["Série 3", "X1", "X3", "Série 1", "320i", "X5", "118i", "X6"],
    "Mercedes-Benz": ["Classe C", "Classe A", "GLA", "GLC", "Sprinter", "C180", "A200"],
    "Audi": ["A3", "A4", "A5", "Q3", "Q5", "Q7", "Q8", "E-tron", "A1", "TT"],
    "Kia": ["Sportage", "Cerato", "Sorento", "Niro", "Stonic", "Picanto", "Rio"],
    "Land Rover": ["Range Rover Evoque", "Discovery", "Defender", "Range Rover Velar", "Range Rover Sport"],
    "Volvo": ["XC40", "XC60", "XC90", "S60", "V60"],
    "RAM": ["1500", "2500", "3500", "Rampage"],
}

CORES_PARA_AGENTE = ["Branco", "Preto", "Prata", "Cinza", "Vermelho", "Azul", "Verde", "Marrom", "Amarelo", "Laranja", "Vinho", "Bege", "Dourado", "Grafite"]
MOTORIZACOES = ["1.0", "1.3", "1.4", "1.5", "1.6", "1.8", "2.0", "1.0 Turbo", "1.4 Turbo", "2.0 Turbo", "2.8 Diesel", "3.2 Diesel"]
TIPOS_VEICULO = ["Passeio", "Hatch", "Sedan", "SUV", "Picape", "Van", "Esportivo"]
OPCIONAIS_LIST = ["Ar condicionado", "Direção hidráulica", "Vidros elétricos", "Travas elétricas", "Alarme", "Som MP3", "Rodas de liga leve", "Teto solar", "Bancos de couro", "Sensor de estacionamento", "Câmera de ré", "Airbag duplo", "Freios ABS", "Farol de neblina", "Controle de estabilidade"]

def normalize_text_for_comparison(text: str):
    # Converte para minúsculas e remove acentos para comparação.
    if not text:
        return ""
    nfkd_form = unicodedata.normalize('NFD', text.lower())
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

class VirtualAgent:
    def __init__(self):
        self.client = MCPClient()
        self.collected_filters = {}
        self.agent_name = "AutoBot"

        self.known_attributes = {
            "marca": {"type": str, "prompt": "Qual marca você prefere?"},
            "modelo": {"type": str, "prompt": "Algum modelo específico em mente?"},
            "ano_fabricacao_min": {"type": int, "prompt": "A partir de que ano de fabricação (ex: 2018)?"},
            "ano_fabricacao_max": {"type": int, "prompt": "Até que ano de fabricação (ex: 2022)?"},
            "ano_modelo_min": {"type": int, "prompt": "A partir de que ano de modelo (ex: 2019)?"},
            "ano_modelo_max": {"type": int, "prompt": "Até que ano de modelo (ex: 2022)?"},
            "combustivel": {"type": CombustivelEnum, "prompt": f"Qual tipo de combustível ({', '.join([c.value for c in CombustivelEnum])})?"},
            "cor": {"type": str, "prompt": "Alguma preferência de cor?"},
            "preco_min": {"type": float, "prompt": "Qual o valor mínimo que você gostaria de investir?"},
            "preco_max": {"type": float, "prompt": "E o valor máximo?"},
            "transmissao": {"type": TransmissaoEnum, "prompt": f"Prefere transmissão ({', '.join([t.value for t in TransmissaoEnum])})?"},
            "num_portas": {"type": int, "prompt": "Quantas portas (2 ou 4, por exemplo)?"},
            "tipo_veiculo": {"type": str, "prompt": "Que tipo de veículo (ex: SUV, Sedan, Hatch)?"}
        }
        
        self.keyword_to_filter_key = {
            "marca": "marca", "fabricante": "marca",
            "modelo": "modelo",
            "ano": "ano_modelo_min", 
            "ano de fabricacao": "ano_fabricacao_min", "ano de fabricação": "ano_fabricacao_min",
            "ano de modelo": "ano_modelo_min",
            "a partir de": "ano_fabricacao_min", "ano minimo": "ano_fabricacao_min", "ano mínimo": "ano_fabricacao_min",
            "ate o ano": "ano_fabricacao_max", "até o ano": "ano_fabricacao_max", "ano maximo": "ano_fabricacao_max", "ano máximo": "ano_fabricacao_max",
            "combustível": "combustivel", "tipo de combustivel": "combustivel", "combustivel": "combustivel",
            "cor": "cor", "pintura": "cor",
            "preço mínimo": "preco_min", "preco minimo": "preco_min", "a partir de r$": "preco_min", "preco de": "preco_min",
            "preço máximo": "preco_max", "preco maximo": "preco_max", "até r$": "preco_max", "valor maximo": "preco_max", "preco ate": "preco_max",
            "transmissão": "transmissao", "transmissao": "transmissao", "cambio": "transmissao", "câmbio": "transmissao",
            "portas": "num_portas",
            "tipo": "tipo_veiculo", "categoria": "tipo_veiculo"
        }

        self.brands_map_lower = {normalize_text_for_comparison(brand): brand for brand in MARCAS_E_MODELOS_PARA_AGENTE.keys()}
        self.models_map_lower = {}
        for brand_orig, models_list in MARCAS_E_MODELOS_PARA_AGENTE.items():
            for model_orig in models_list:
                self.models_map_lower[normalize_text_for_comparison(model_orig)] = (brand_orig, model_orig)
        self.colors_map_lower = {normalize_text_for_comparison(color): color for color in CORES_PARA_AGENTE}

    def _parse_direct_entities(self, words_lower_normalized: list, words_original_case: list, extracted: dict, consumed_indices: list):
        # Tenta identificar MARCA (até 2 palavras)
        if "marca" not in extracted:
            for n_words in range(min(2, len(words_lower_normalized)), 0, -1):
                for i in range(len(words_lower_normalized) - n_words + 1):
                    if any(consumed_indices[k] for k in range(i, i + n_words)): continue
                    potential_entity = " ".join(words_lower_normalized[i : i + n_words])
                    if potential_entity in self.brands_map_lower:
                        extracted["marca"] = self.brands_map_lower[potential_entity]
                        for k in range(i, i + n_words): consumed_indices[k] = True
                        break
                if "marca" in extracted: break
        
        # Tenta identificar MODELO (até 2 palavras), considerando a marca se já encontrada
        if "modelo" not in extracted:
            current_brand_in_filters = extracted.get("marca")
            for n_words in range(min(2, len(words_lower_normalized)), 0, -1):
                for i in range(len(words_lower_normalized) - n_words + 1):
                    if any(consumed_indices[k] for k in range(i, i + n_words)): continue
                    potential_entity = " ".join(words_lower_normalized[i : i + n_words])
                    if potential_entity in self.models_map_lower:
                        brand_of_model, model_name = self.models_map_lower[potential_entity]
                        if current_brand_in_filters and current_brand_in_filters != brand_of_model:
                            # Modelo encontrado não pertence à marca já identificada, pode ser um falso positivo.
                            # Ou a marca identificada anteriormente estava errada.
                            # Por ora, se a marca já existe e é diferente, não pegamos este modelo.
                            continue
                        
                        extracted["modelo"] = model_name
                        if not current_brand_in_filters: # Inferir marca se não foi pega antes
                            extracted["marca"] = brand_of_model
                        
                        for k in range(i, i + n_words): consumed_indices[k] = True
                        break
                if "modelo" in extracted: break

        # Tenta identificar COR (palavra única)
        if "cor" not in extracted:
            for i, word_norm in enumerate(words_lower_normalized):
                if consumed_indices[i]: continue
                if word_norm in self.colors_map_lower:
                    extracted["cor"] = self.colors_map_lower[word_norm]
                    consumed_indices[i] = True
                    break
        
        # Tenta identificar ANO (simples: número de 4 dígitos)
        if "ano_modelo_min" not in extracted and "ano_fabricacao_min" not in extracted:
            for i, word_orig in enumerate(words_original_case): # Usa original para checar se é dígito
                if consumed_indices[i]: continue
                if re.fullmatch(r"(19[89]\d|20\d{2})", word_orig): # Anos de 1980-2099
                    year_val = int(word_orig)
                    extracted["ano_modelo_min"] = year_val
                    if "ano_modelo_max" not in extracted: # Se max não foi setado por range keyword
                        extracted["ano_modelo_max"] = year_val # Assume ano exato
                    consumed_indices[i] = True
                    break

    def _parse_keyword_entities(self, text: str, extracted: dict):
        text_lower_normalized = normalize_text_for_comparison(text) # Normaliza o texto inteiro para keywords

        # Ranges primeiro
        range_patterns = {
            "ano_fabricacao": (r"ano (?:de fabricacao|fabricacao|fab)\s*(?:entre|de)\s*(\d{4})\s*(?:a|e)\s*(\d{4})", "ano_fabricacao_min", "ano_fabricacao_max"),
            "ano_modelo": (r"ano (?:de modelo|modelo)\s*(?:entre|de)\s*(\d{4})\s*(?:a|e)\s*(\d{4})", "ano_modelo_min", "ano_modelo_max"),
            "preco": (r"(?:preco|valor)\s*(?:entre|de)\s*([\d\.,]+)\s*(?:a|e)\s*([\d\.,]+)", "preco_min", "preco_max") # Aceita . e ,
        }
        
        temp_text_for_ranges = text_lower_normalized
        for key_type, (pattern, min_key, max_key) in range_patterns.items():
            match = re.search(pattern, temp_text_for_ranges)
            if match:
                try:
                    val1_str = match.group(1).replace(",", "") # Remove vírgula para int/float
                    val2_str = match.group(2).replace(",", "")
                    
                    val1 = float(val1_str) if key_type == "preco" else int(val1_str)
                    val2 = float(val2_str) if key_type == "preco" else int(val2_str)
                    
                    if min_key not in extracted: extracted[min_key] = min(val1, val2)
                    if max_key not in extracted: extracted[max_key] = max(val1, val2)
                    temp_text_for_ranges = temp_text_for_ranges.replace(match.group(0), "", 1)
                except ValueError:
                    pass

        # Keywords individuais
        sorted_keywords_normalized = sorted(
            [normalize_text_for_comparison(kw) for kw in self.keyword_to_filter_key.keys()],
            key=len,
            reverse=True
        )
        
        # Mapeia keyword normalizada para a chave de filtro original
        normalized_kw_to_filter_key = {
            normalize_text_for_comparison(kw): self.keyword_to_filter_key[kw] 
            for kw in self.keyword_to_filter_key
        }

        text_for_keyword_search = temp_text_for_ranges

        for norm_keyword in sorted_keywords_normalized:
            filter_key = normalized_kw_to_filter_key[norm_keyword]
            if filter_key in extracted and not (filter_key.endswith("_min") or filter_key.endswith("_max")):
                if not (norm_keyword == normalize_text_for_comparison("ano") and filter_key == "ano_modelo_min"):
                    continue
            lookahead_keywords = r"marca|modelo|ano|cor|preco|valor|transmissao|cambio|portas|tipo|combustivel|fabricante|categoria"
            pattern_str = rf"\b{re.escape(norm_keyword)}\b\s*[:e\s]*\s*((?:(?!\b(?:{lookahead_keywords})\b).)+?)(?:\s*(?:\b(?:{lookahead_keywords})\b|$)|,)"
            if "_min" in filter_key or "_max" in filter_key or filter_key == "num_portas":
                 pattern_str = rf"\b{re.escape(norm_keyword)}\b\s*[:e\s]*\s*([\d\.,]+)"
    
            match = re.search(pattern_str, text_for_keyword_search, re.IGNORECASE)

            if match:
                value_str_raw = match.group(1).strip()
                if not value_str_raw: continue

                attr_config = self.known_attributes.get(filter_key)
                processed_value = None
                try:
                    if attr_config:
                        if attr_config["type"] == int:
                            processed_value = int(re.sub(r'[^\d]', '', value_str_raw))
                        elif attr_config["type"] == float:
                            processed_value = float(re.sub(r'[^\d\.]', '', value_str_raw.replace(',', '.')))
                        elif attr_config["type"] in [CombustivelEnum, TransmissaoEnum]:
                            normalized_input_val = normalize_text_for_comparison(value_str_raw)
                            for enum_member in attr_config["type"]:
                                if normalize_text_for_comparison(enum_member.value) == normalized_input_val:
                                    processed_value = enum_member.value
                                    break
                            if processed_value is None: continue
                        else: # String
                            processed_value = value_str_raw # Mantém a capitalização original da entrada
                    else: 
                        if value_str_raw.isdigit() and filter_key.startswith("ano_"):
                            processed_value = int(value_str_raw)
                        else:
                            processed_value = value_str_raw
                    
                    if filter_key not in extracted:
                        extracted[filter_key] = processed_value
                        if norm_keyword == normalize_text_for_comparison("ano") and filter_key == "ano_modelo_min" and "ano_modelo_max" not in extracted:
                            if not re.search(r"ano (?:de modelo|modelo)\s*(?:entre|de)\s*\d{4}\s*(?:a|e)\s*\d{4}", text_lower_normalized):
                                extracted["ano_modelo_max"] = processed_value
                        
                        try:
                            text_for_keyword_search = text_for_keyword_search.replace(match.group(0), "", 1)
                        except IndexError: pass
                except ValueError:
                    pass

    def _parse_user_input(self, text: str):
        extracted = {}
        words_original_case = text.split()
        # Normaliza (lowercase + remove acentos) para comparações 
        words_lower_normalized = [normalize_text_for_comparison(w) for w in words_original_case]
        consumed_indices = [False] * len(words_lower_normalized)

        #Reconhecimento direto de entidades (marca, modelo, cor, ano simples)
        self._parse_direct_entities(words_lower_normalized, words_original_case, extracted, consumed_indices)
        # Esta etapa opera sobre o texto original e pode refinar ou adicionar filtros,
        self._parse_keyword_entities(text, extracted) # Passa o texto original
        
        return extracted

    def _ask_clarifying_questions(self):
        for key_being_asked, attr_info in self.known_attributes.items():
            if key_being_asked not in self.collected_filters:
                if key_being_asked == "modelo" and "marca" not in self.collected_filters: continue
                if key_being_asked == "ano_fabricacao_max" and "ano_fabricacao_min" not in self.collected_filters: continue
                if key_being_asked == "ano_modelo_max" and "ano_modelo_min" not in self.collected_filters: continue
                if key_being_asked == "preco_max" and "preco_min" not in self.collected_filters: continue

                user_response_raw = input(f"{self.agent_name}: {attr_info['prompt']} (ou digite 'pular'/'buscar') ").strip()
                user_response_lower = user_response_raw.lower()

                if user_response_lower == 'buscar': return "buscar"
                if user_response_lower == 'pular' or not user_response_raw: continue

                processed_directly = False
                converted_value = None
                if user_response_raw:
                    try:
                        if attr_info["type"] == int:
                            if re.fullmatch(r"\d+", user_response_raw):
                                converted_value = int(user_response_raw)
                                processed_directly = True
                        elif attr_info["type"] == float:
                            if re.fullmatch(r"[\d\.,]+", user_response_raw):
                                converted_value = float(re.sub(r'[^\d\.]', '', user_response_raw.replace(',', '.')))
                                processed_directly = True
                        elif attr_info["type"] in [CombustivelEnum, TransmissaoEnum]:
                            normalized_input = normalize_text_for_comparison(user_response_raw)
                            for enum_member in attr_info["type"]:
                                if normalize_text_for_comparison(enum_member.value) == normalized_input:
                                    converted_value = enum_member.value
                                    processed_directly = True
                                    break
                        elif attr_info["type"] == str:
                            if user_response_lower not in ['buscar', 'pular', 'limpar', 'adicionar', 'sair', 'nao sei', 'não sei', 'tanto faz']:
                                converted_value = user_response_raw # Mantém capitalização original
                                processed_directly = True
                    except ValueError: pass

                if processed_directly and converted_value is not None:
                    self.collected_filters[key_being_asked] = converted_value
                    print(f"{self.agent_name}: Entendido: {key_being_asked.replace('_', ' ').capitalize()} = {converted_value}.")
                else:
                    newly_parsed_filters = self._parse_user_input(user_response_raw)
                    if newly_parsed_filters:
                        any_filter_applied_from_complex_response = False
                        for pk, pv in newly_parsed_filters.items():
                            self.collected_filters[pk] = pv
                            print(f"{self.agent_name}: Entendido (da sua resposta): {pk.replace('_', ' ').capitalize()} = {pv}.")
                            any_filter_applied_from_complex_response = True
                        if not any_filter_applied_from_complex_response and user_response_lower not in ['pular', 'buscar', 'não sei', 'nao sei', 'tanto faz']:
                             print(f"{self.agent_name}: Humm, não consegui extrair informações válidas de '{user_response_raw}' para a pergunta.")
                    elif user_response_lower not in ['pular', 'buscar', 'não sei', 'nao sei', 'tanto faz']:
                        print(f"{self.agent_name}: Desculpe, não entendi bem '{user_response_raw}' como resposta para '{attr_info['prompt']}'. Tente novamente ou 'pular'.")
        return "continuar"

    def greet(self):
        print(f"{self.agent_name}: Olá! Sou seu assistente virtual para busca de veículos.")
        print(f"{self.agent_name}: Você pode me dizer o que procura, por exemplo: 'um Volvo XC90 2024 Vermelho'")
        print(f"{self.agent_name}: Quando quiser buscar, diga 'buscar'. Para limpar filtros, diga 'limpar'. Para sair, 'sair'.")

    def run_interaction_loop(self):
        if not self.client.connect():
            print(f"{self.agent_name}: Não consegui me conectar ao sistema de busca. Tente novamente mais tarde.")
            return
        self.greet()
        while True:
            user_input_raw = input("Você: ").strip()
            user_input_lower = user_input_raw.lower()
            if not user_input_raw: continue
            if user_input_lower == 'sair':
                print(f"{self.agent_name}: Até logo! Volte sempre. Muito Obrigado - Feito por Flávio Machado de Sousa"); break
            if user_input_lower == 'limpar':
                self.collected_filters.clear()
                print(f"{self.agent_name}: Filtros limpos. O que você procura agora?"); continue

            perform_search_now = False
            if user_input_lower == 'buscar':
                if not self.collected_filters:
                    print(f"{self.agent_name}: Precisamos de pelo menos um filtro para buscar."); continue
                perform_search_now = True
            else:
                new_filters = self._parse_user_input(user_input_raw)
                if new_filters:
                    for k, v in new_filters.items(): self.collected_filters[k] = v
                    print(f"{self.agent_name}: Entendi. Filtros atuais são: {self.collected_filters}")
                else:
                    if not any(kw in user_input_lower for kw in ["obrigado", "ok", "valeu", "entendi", "certo", "sim", "nao"]):
                        print(f"{self.agent_name}: Humm, não captei nenhum filtro específico disso. Pode tentar de novo ou dizer 'buscar' se os filtros atuais estiverem corretos.")

            if not perform_search_now and self.collected_filters:
                prompt_action = input(f"{self.agent_name}: Deseja 'buscar' com os filtros atuais, 'adicionar' mais detalhes, ou 'limpar' e recomeçar? ").strip().lower()
                if prompt_action == 'buscar': perform_search_now = True
                elif prompt_action == 'limpar':
                    self.collected_filters.clear(); print(f"{self.agent_name}: Filtros limpos. O que você procura?"); continue
                elif prompt_action == 'adicionar':
                    action_result = self._ask_clarifying_questions()
                    if action_result == "buscar": perform_search_now = True
                    else: continue # Volta para o input principal para o usuário adicionar mais ou buscar

            if perform_search_now and self.collected_filters:
                print(f"{self.agent_name}: Ok, buscando veículos com os seguintes critérios: {self.collected_filters}")
                final_filters_for_request = self.collected_filters.copy() # Envia uma cópia
                
                if not self.client.sock:
                    if not self.client.connect():
                        print(f"{self.agent_name}: Falha ao reconectar ao servidor MCP. Tente 'buscar' novamente."); continue
                
                response = self.client.query_vehicles(final_filters_for_request)
                if response and response.get("status") == "success":
                    vehicles = response.get("data", [])
                    if vehicles:
                        print(f"\n{self.agent_name}: Encontrei {len(vehicles)} veículo(s) para você:\n")
                        for car_idx, car in enumerate(vehicles):
                            if car_idx >= 5 and len(vehicles) > 5:
                                print(f"... e mais {len(vehicles) - 5} veículo(s). Refine sua busca se necessário."); break
                            print(f"  - {car.get('marca','N/A')} {car.get('modelo','N/A')} {car.get('ano_modelo','N/A')}")
                            print(f"    Cor: {car.get('cor','N/A')}, KM: {car.get('quilometragem','N/A')}, Preço: R$ {car.get('preco','N/A'):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                            print(f"    Combustível: {car.get('combustivel','N/A')}, Câmbio: {car.get('transmissao','N/A')}, Portas: {car.get('num_portas','N/A')}")
                            opcionais_str = car.get('opcionais', '')
                            if opcionais_str: print(f"    Opcionais: {opcionais_str[:70]}...\n" if len(opcionais_str) > 70 else f"    Opcionais: {opcionais_str}\n")
                            else: print("")
                    else:
                        print(f"{self.agent_name}: Puxa, não encontrei veículos com esses critérios. Quer tentar outros filtros (diga 'limpar') ou ajustar os atuais?")
                else:
                    error_msg = response.get('message', 'Erro desconhecido do servidor.')
                    print(f"{self.agent_name}: Desculpe, tive um problema ao buscar: {error_msg}")
            elif perform_search_now and not self.collected_filters:
                 print(f"{self.agent_name}: Precisamos de alguns filtros para buscar. O que você tem em mente?")
        self.client.close()
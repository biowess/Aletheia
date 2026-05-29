from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class PreprocessingResult(BaseModel):
    """
    Pydantic schema representing the deterministic findings
    from the preprocessing engine.
    """
    anemia_classification: Optional[str] = None
    cytopenias: List[str] = []
    inflammatory_pattern: Optional[str] = None
    metabolic_flags: List[str] = []
    interpretations: List[str] = []

class PreprocessingEngine:
    """
    A pure Python, no-AI module that interprets structured clinical data
    and derives medically meaningful classifications from laboratory values
    and clinical patterns using deterministic keyword/regex heuristics.
    
    Architectural Note:
    Deterministic-first, AI-second pipeline design ensures that well-defined
    clinical heuristics are processed reliably and cheaply, providing context
    to the LLM. This reduces token usage, minimizes AI hallucination on 
    routine lab analysis, and grounds the reasoning engine in established 
    medical patterns.
    """

    def _classify_anemia(self, lab_data: Dict[str, Any]) -> Optional[str]:
        """
        Classify anemia based on hemoglobin and MCV mentions.
        This is a deterministic heuristic approximation.
        """
        cbc = str(lab_data.get("cbc", "")).lower()
        if not cbc:
            return None
            
        # Check for hemoglobin references indicating anemia
        if "low hemoglobin" in cbc or "anemia" in cbc:
            # Check MCV for morphological classification
            if "low mcv" in cbc or "microcytic" in cbc:
                return "microcytic hypochromic anemia"
            elif "high mcv" in cbc or "macrocytic" in cbc:
                return "macrocytic anemia"
            else:
                return "normocytic normochromic anemia"
        return None

    def _detect_cytopenias(self, lab_data: Dict[str, Any]) -> List[str]:
        """
        Detect specific cytopenias based on keyword matching in CBC.
        """
        cbc = str(lab_data.get("cbc", "")).lower()
        if not cbc:
            return []
            
        detected = []
        keywords = ["thrombocytopenia", "leukopenia", "neutropenia", "pancytopenia"]
        for kw in keywords:
            if kw in cbc:
                detected.append(kw)
        return detected

    def _classify_inflammatory_pattern(self, lab_data: Dict[str, Any]) -> Optional[str]:
        """
        Classify inflammatory pattern based on markers.
        """
        markers = str(lab_data.get("inflammatory_markers", "")).lower()
        if not markers:
            return None
            
        elevated_keywords = [
            "elevated crp", "high crp", 
            "elevated esr", "high esr", 
            "elevated ferritin", "high ferritin", 
            "elevated fibrinogen", "high fibrinogen"
        ]
        
        has_elevation = any(kw in markers for kw in elevated_keywords) or \
                        (any(marker in markers for marker in ["crp", "esr", "ferritin", "fibrinogen"]) and "elevated" in markers)
        
        if has_elevation:
            if "chronic" in markers:
                return "chronic inflammatory pattern"
            else:
                # Default to acute if unspecified but elevated markers are present
                return "acute inflammatory pattern"
                
        return None

    def _detect_metabolic_flags(self, lab_data: Dict[str, Any]) -> List[str]:
        """
        Detect metabolic anomalies based on chemistry panel keywords.
        """
        chem = str(lab_data.get("chemistry", "")).lower()
        if not chem:
            return []
            
        flags = []
        keywords = [
            "elevated creatinine", 
            "elevated bilirubin", 
            "elevated ldh", 
            "hypoalbuminemia", 
            "elevated transaminases"
        ]
        
        for kw in keywords:
            if kw in chem:
                flags.append(kw)
        return flags

    def _generate_interpretations(self, result: Dict[str, Any]) -> List[str]:
        """
        Synthesize findings into human-readable clinical interpretations.
        """
        interpretations = []
        
        anemia = result.get("anemia_classification")
        inflam = result.get("inflammatory_pattern")
        cyto = result.get("cytopenias", [])
        metab = result.get("metabolic_flags", [])
        
        # Rule: Microcytic anemia + inflammatory markers
        if anemia == "microcytic hypochromic anemia" and inflam:
            interpretations.append("Microcytic anemia with elevated inflammatory markers suggests iron deficiency or anemia of chronic disease")
            
        # Rule: Pancytopenia + elevated LDH
        if "pancytopenia" in cyto and "elevated ldh" in metab:
            interpretations.append("Pancytopenia with elevated LDH may suggest bone marrow pathology")
            
        return interpretations

    def run(self, lab_data: Dict[str, Any], physical_exam: Dict[str, Any], anamnesis: Dict[str, Any]) -> PreprocessingResult:
        """
        Execute all deterministic sub-analyzers and synthesize results.
        
        Args:
            lab_data: Dictionary of laboratory findings (e.g., cbc, chemistry)
            physical_exam: Dictionary of physical examination findings
            anamnesis: Dictionary of patient history and symptoms
            
        Returns:
            PreprocessingResult schema instance containing extracted classifications.
        """
        # Ensure safe defaults if None is passed
        lab_data = lab_data or {}
        physical_exam = physical_exam or {}
        anamnesis = anamnesis or {}
        
        # Execute sub-analyzers
        anemia_class = self._classify_anemia(lab_data)
        cytopenias = self._detect_cytopenias(lab_data)
        inflam_pattern = self._classify_inflammatory_pattern(lab_data)
        metabolic_flags = self._detect_metabolic_flags(lab_data)
        
        # Construct temporary result dict for interpretation generation
        temp_result = {
            "anemia_classification": anemia_class,
            "cytopenias": cytopenias,
            "inflammatory_pattern": inflam_pattern,
            "metabolic_flags": metabolic_flags
        }
        
        # Generate synthesis
        interpretations = self._generate_interpretations(temp_result)
        
        return PreprocessingResult(
            anemia_classification=anemia_class,
            cytopenias=cytopenias,
            inflammatory_pattern=inflam_pattern,
            metabolic_flags=metabolic_flags,
            interpretations=interpretations
        )

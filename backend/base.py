# app/nodes/base.py
from typing import Dict, Any

class BaseNode:
    """
    Classe de base pour tous les nœuds LCNC.
    Tout nœud (trigger ou action) doit hériter de cette classe.
    """

    def execute(
        self,
        configuration: Dict[str, Any],
        context: Dict[str, Any],
        test_mode: bool = False
    ) -> Any:
        """
        Méthode principale à surcharger par chaque nœud.

        - configuration : dict contenant la configuration du nœud (ex: filtres, access_token…)
        - context : dict contenant le contexte du workflow (ex: trigger_data, variables…)
        - test_mode : bool pour retourner des données simulées si True
        """
        raise NotImplementedError("Chaque nœud doit implémenter la méthode execute")

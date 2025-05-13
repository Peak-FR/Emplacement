function toggleSideNav() {
    const sideNav = document.getElementById("sideNav");
    const mainContent = document.getElementById("mainContent");
    const mobileToggle = document.querySelector(".mobile-menu-toggle");

    if (sideNav.style.width === "250px" || sideNav.classList.contains("open")) {
        sideNav.style.width = "0";
        sideNav.classList.remove("open");
    } else {
        sideNav.style.width = "250px";
        sideNav.classList.add("open");
    }
}

function closeSideNavIfMobile() {
    const sideNav = document.getElementById("sideNav");
    const mobileToggle = document.querySelector(".mobile-menu-toggle");
    if (mobileToggle && getComputedStyle(mobileToggle).display !== "none") {
        if (sideNav.classList.contains("open")) {
            sideNav.style.width = "0";
            sideNav.classList.remove("open");
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('sectionAccueil')) {
        showSection('sectionAccueil');
        chargerStatistiquesAccueil();
    } else {
        showSection('sectionPlan');
    }
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', async function () {
            try {
                const response = await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.href = '/connexion';
                } else {
                    alert('Erreur lors de la déconnexion: ' + (data.erreur || response.statusText));
                }
            } catch (error) {
                console.error('Erreur réseau ou autre lors de la déconnexion:', error);
                alert('Erreur réseau lors de la déconnexion. Veuillez vérifier votre connexion et réessayer.');
            }
        });
    }

    const batchAssignTextarea = document.getElementById('batchAssignProductsTextarea');
    const batchLiberateTextarea = document.getElementById('batchLiberateIdsTextarea');

    if (batchAssignTextarea) {
        batchAssignTextarea.addEventListener('keydown', function (e) {
            if (e.key === 'Tab' || e.keyCode === 9) {
                e.preventDefault();

                const start = this.selectionStart;
                const end = this.selectionEnd;
                this.value = this.value.substring(0, start) + '\t' + this.value.substring(end);

                this.selectionStart = this.selectionEnd = start + 1;
            }
        });
    }

    if (batchLiberateTextarea) {
        batchLiberateTextarea.addEventListener('keydown', function (e) {
            if (e.key === 'Tab' || e.keyCode === 9) {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                this.value = this.value.substring(0, start) + '\t' + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + 1;
            }
        });
    }
    checkLoginStatus();
});

async function checkLoginStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        const nomUtilisateurConnecteEl = document.getElementById('nomUtilisateurConnecte');

        if (data.connecte) {
            if (nomUtilisateurConnecteEl) {
                nomUtilisateurConnecteEl.textContent = `Connecté en tant que ${data.utilisateur}`;
            }
            // Si l'utilisateur est connecté et sur la page de connexion, rediriger vers l'accueil
            if (window.location.pathname === '/connexion' || window.location.pathname === '/connexion/') {
                window.location.href = '/';
            }
        } else {
            if (nomUtilisateurConnecteEl) {
                nomUtilisateurConnecteEl.textContent = 'Non connecté';
            }
            // Si l'utilisateur n'est pas connecté et n'est pas sur la page de connexion, rediriger
            if (window.location.pathname !== '/connexion' && window.location.pathname !== '/connexion/') {
                window.location.href = '/connexion';
            }
        }
    } catch (error) {
        console.error('Erreur lors de la vérification du statut de connexion:', error);
        // Gérer le cas où l'API n'est pas joignable (ne pas rediriger en boucle)
        if (window.location.pathname !== '/connexion' && window.location.pathname !== '/connexion/') {
            // Peut-être afficher un message à l'utilisateur au lieu de rediriger
            // pour éviter des boucles si le serveur est en panne.
        }
    }
}

function showSection(sectionIdToShow) {
    const sections = document.querySelectorAll('#mainContent .container .section');
    sections.forEach(section => {
        section.classList.add('hidden');
    });

    const activeSection = document.getElementById(sectionIdToShow);
    if (activeSection) {
        activeSection.classList.remove('hidden');
    } else {
        console.error(`Section avec ID '${sectionIdToShow}' non trouvée.`);
    }

    if (sectionIdToShow === 'sectionAccueil') {
        chargerStatistiquesAccueil();
    }

    const navLinks = document.querySelectorAll('#sideNav a');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + sectionIdToShow) {
            link.classList.add('active');
        }
    });
    closeSideNavIfMobile();

    const assignationForm = document.getElementById('assignationFormSection');
    if (assignationForm) {
        if (sectionIdToShow !== 'sectionConsulter' &&
            sectionIdToShow !== 'sectionTrouver' &&
            !(activeSection && activeSection.contains(assignationForm)) &&
            sectionIdToShow !== 'sectionPlan') {
            assignationForm.classList.add('hidden');
        }
        if (sectionIdToShow === 'sectionAccueil' || sectionIdToShow === 'sectionPlan' || sectionIdToShow === 'sectionAssignerRapide' || sectionIdToShow === 'sectionAssignerMasse' || sectionIdToShow === 'sectionLibererMasse' || sectionIdToShow === 'sectionHistorique' || sectionIdToShow === 'sectionStatistiques') {
            assignationForm.classList.add('hidden');
        }
    }
}

// Core fonctions
function afficherDetailsEmplacement(data, targetDivId) {
    const detailsDiv = document.getElementById(targetDivId);
    const assignationFormSection = document.getElementById('assignationFormSection');
    const assignEmplacementIdLabel = document.getElementById('assignEmplacementIdLabel');
    const assignEmplacementIdHidden = document.getElementById('assignEmplacementIdHidden');
    const assignationResultDiv = document.getElementById('assignationResult');

    if (!detailsDiv || !assignationFormSection || !assignEmplacementIdLabel || !assignEmplacementIdHidden || !assignationResultDiv) {
        console.error("Un ou plusieurs éléments HTML pour l'affichage des détails ou l'assignation sont manquants.");
        return;
    }

    let htmlContent = `<h3>Détails pour ${data.id_emplacement_str}</h3>`;
    htmlContent += `<ul>
                        <li>Taille: ${data.taille}</li>
                        <li>Allée: ${data.allee_lettre}</li>
                        <li>Rack: ${data.rack_numero}</li>
                        <li>Niveau: ${data.niveau}</li>
                        <li>Position: ${data.position_dans_niveau}</li>
                        <li>Libre: ${data.est_libre ? 'Oui' : 'Non'}</li>`;
    if (!data.est_libre) {
        htmlContent += `<li>Produit: ${data.produit_nom || 'N/A'} (ID: ${data.produit_id || 'N/A'})</li>`;
        htmlContent += `</ul><button onclick="submitLiberation('${data.id_emplacement_str}', '${targetDivId}')">Libérer cet Emplacement</button>`;
    } else {
        htmlContent += `</ul>`;
    }
    detailsDiv.innerHTML = htmlContent;

    if (data.est_libre) {
        assignEmplacementIdLabel.textContent = data.id_emplacement_str;
        assignEmplacementIdHidden.value = data.id_emplacement_str;
        assignationFormSection.classList.remove('hidden');
        assignationResultDiv.innerHTML = "";
        document.getElementById('assignNomProduit').value = "";
        document.getElementById('assignIdProduit').value = "";
    } else {
        assignationFormSection.classList.add('hidden');
    }
}

async function getEmplacementDetails() {
    const emplacementId = document.getElementById('emplacementIdInput').value;
    const detailsDiv = document.getElementById('detailsEmplacement');
    const assignationFormSection = document.getElementById('assignationFormSection');

    if (!emplacementId) {
        detailsDiv.innerHTML = '<p class="error-message">Veuillez entrer un ID d_emplacement.</p>';
        if (assignationFormSection) assignationFormSection.classList.add('hidden');
        return;
    }
    detailsDiv.innerHTML = '<p>Chargement...</p>';
    if (assignationFormSection) assignationFormSection.classList.add('hidden');

    try {
        const response = await fetch(`/api/emplacements/${emplacementId}`);
        if (response.ok) {
            const data = await response.json();
            afficherDetailsEmplacement(data, 'detailsEmplacement');
        } else {
            const errorData = await response.json();
            detailsDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${errorData.erreur || response.statusText}</p>`;
        }
    } catch (error) {
        console.error('Erreur lors de la récupération des détails:', error);
        detailsDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur.</p>`;
    }
}

async function findOptimalEmplacementShared(isAlleeJOnly) {
    const tailleSelected = document.getElementById('tailleRequiseSelect').value;
    const exclureJ = document.getElementById('exclureAlleeJCheck').checked;
    const eparpillementTotal = document.getElementById('eparpillageTotalCheck').checked;
    const resultDiv = document.getElementById('optimalEmplacementResult');
    const assignationFormSection = document.getElementById('assignationFormSection');

    let taillePourRecherche;
    let messageChargement;

    if (isAlleeJOnly) {
        taillePourRecherche = "Moyen";
        messageChargement = `<p>Recherche en cours (Allée J, Taille: ${taillePourRecherche})...</p>`;
    } else {
        taillePourRecherche = tailleSelected;
        messageChargement = '<p>Recherche en cours...</p>';
    }

    if (resultDiv) {
        resultDiv.innerHTML = messageChargement;
    }
    if (assignationFormSection) {
        assignationFormSection.classList.add('hidden');
    }

    const queryParams = new URLSearchParams({
        taille: taillePourRecherche,
    });

    if (isAlleeJOnly) {
        queryParams.append('chercher_seulement_allee_J', true);
    } else {
        queryParams.append('exclure_allee_J', exclureJ);
        queryParams.append('eparpillage_total', eparpillementTotal);
    }

    try {
        const response = await fetch(`/api/emplacements/optimal-libre?${queryParams.toString()}`);
        if (response.ok) {
            const data = await response.json();
            afficherDetailsEmplacement(data, 'optimalEmplacementResult');

            const h3Optimal = document.querySelector('#optimalEmplacementResult h3');
            if (h3Optimal) {
                h3Optimal.textContent = `Emplacement optimal trouvé${isAlleeJOnly ? ' en Allée J' : ''} : ${data.id_emplacement_str}`;
            }
        } else if (response.status === 404) {
            const errorData = await response.json();
            if (resultDiv) resultDiv.innerHTML = `<p class="info-message">${errorData.message || "Aucun emplacement libre trouvé pour ces critères."}</p>`;
        } else {
            const errorData = await response.json();
            if (resultDiv) resultDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${errorData.erreur || response.statusText}</p>`;
        }
    } catch (error) {
        console.error('Erreur lors de la recherche d_emplacement optimal:', error);
        if (resultDiv) resultDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur.</p>`;
    }
}

function findOptimalEmplacement() {
    findOptimalEmplacementShared(false);
}

function findOptimalInAlleeJ() {
    findOptimalEmplacementShared(true);
}

async function submitAssignation() {
    const emplacementId = document.getElementById('assignEmplacementIdHidden').value;
    const nomProduit = document.getElementById('assignNomProduit').value;
    const idProduit = document.getElementById('assignIdProduit').value;
    const assignationResultDiv = document.getElementById('assignationResult');

    if (!emplacementId) {
        assignationResultDiv.innerHTML = '<p class="error-message">Erreur : ID d_emplacement cible non défini.</p>';
        return;
    }
    if (!nomProduit || !idProduit) {
        assignationResultDiv.innerHTML = '<p class="error-message">Veuillez entrer le nom ET l_ID du produit.</p>';
        return;
    }

    assignationResultDiv.innerHTML = '<p>Assignation en cours...</p>';

    const payload = { nom_produit: nomProduit };
    if (idProduit) {
        payload.id_produit = idProduit;
    }

    try {
        const response = await fetch(`/api/emplacements/${emplacementId}/assigner`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const responseData = await response.json();

        if (response.ok) {
            assignationResultDiv.innerHTML = `<p class="info-message">${responseData.message}</p>`;
            document.getElementById('assignationFormSection').classList.add('hidden');

            const detailsDiv = document.getElementById('detailsEmplacement');
            const optimalResultDiv = document.getElementById('optimalEmplacementResult');

            if (detailsDiv && detailsDiv.innerHTML.includes(emplacementId)) {
                getEmplacementDetails();
            } else if (optimalResultDiv && optimalResultDiv.innerHTML.includes(emplacementId)) {
                optimalResultDiv.innerHTML = "<p>L'emplacement précédemment suggéré a été assigné. Effectuez une nouvelle recherche.</p>";
                if (document.getElementById('emplacementIdInput').value === emplacementId) {
                    getEmplacementDetails();
                }
            }
        } else {
            assignationResultDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${responseData.erreur || response.statusText}</p>`;
        }
    } catch (error) {
        console.error('Erreur lors de l_assignation:', error);
        assignationResultDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur pour l_assignation.</p>`;
    }
}

async function submitQuickAssignProduct() {
    const nomProduit = document.getElementById('quickAssignNomProduit').value;
    const idProduit = document.getElementById('quickAssignIdProduit').value;
    const tailleRequise = document.getElementById('quickAssignTailleRequise').value;
    const exclureJ = document.getElementById('quickAssignExclureJ').checked;
    const eparpillementTotal = document.getElementById('quickAssignEparpillementTotal').checked;
    const resultDiv = document.getElementById('quickAssignResult');

    if (!nomProduit || !idProduit) {
        resultDiv.innerHTML = '<p class="error-message">Veuillez entrer le nom ET l_ID du produit.</p>';
        return;
    }

    resultDiv.innerHTML = '<p>Recherche d_emplacement et assignation en cours...</p>';

    const produitData = {
        nom_produit: nomProduit,
        taille_requise: tailleRequise
    };
    if (idProduit) {
        produitData.id_produit = idProduit;
    }

    const payload = {
        produits_a_assigner: [produitData],
        exclure_allee_J: exclureJ,
        mode_eparpillage_total_global: eparpillementTotal
    };

    try {
        const response = await fetch(`/api/emplacements/assigner-en-masse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const responseData = await response.json();

        if (response.ok && responseData.details_assignations && responseData.details_assignations.length > 0) {
            const assignationDetail = responseData.details_assignations[0];
            if (assignationDetail.statut === "Assigné") {
                resultDiv.innerHTML = `<p class="info-message">Produit '${assignationDetail.produit_nom}' assigné avec succès à l'emplacement <strong style="font-size:1.1em;">${assignationDetail.emplacement_assigne}</strong>.</p>`;
                document.getElementById('quickAssignNomProduit').value = '';
                document.getElementById('quickAssignIdProduit').value = '';
            } else {
                resultDiv.innerHTML = `<p class="error-message">Échec de l'assignation pour '${assignationDetail.produit_nom}': ${assignationDetail.message}</p>`;
            }
        } else if (responseData.erreur) {
            resultDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${responseData.erreur || 'Erreur inconnue du serveur.'}</p>`;
        } else {
            resultDiv.innerHTML = `<p class="error-message">Réponse inattendue du serveur (Statut ${response.status}). Veuillez vérifier la console du navigateur.</p>`;
        }
    } catch (error) {
        console.error('Erreur lors de l_assignation rapide:', error);
        resultDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur pour l_assignation rapide.</p>`;
    }
}

async function submitLiberation(emplacementId, resultDisplayDivId = null) {
    const resultTargetDiv = document.getElementById(resultDisplayDivId || 'assignationResult');
    if (!resultTargetDiv && resultDisplayDivId) {
        console.error(`Div de résultat '${resultDisplayDivId}' non trouvée pour la libération.`);
        return;
    }

    if (!emplacementId) {
        if (resultTargetDiv) resultTargetDiv.innerHTML = '<p class="error-message">Erreur : ID d_emplacement non fourni pour la libération.</p>';
        console.error("ID d'emplacement non fourni pour submitLiberation");
        return;
    }

    if (resultTargetDiv) resultTargetDiv.innerHTML = `<p>Libération de ${emplacementId} en cours...</p>`;

    try {
        const response = await fetch(`/api/emplacements/${emplacementId}/liberer`, {
            method: 'POST',
        });
        const responseData = await response.json();

        if (response.ok) {
            if (resultTargetDiv) resultTargetDiv.innerHTML = `<p class="info-message">${responseData.message}</p>`;

            const detailsDiv = document.getElementById('detailsEmplacement');
            const optimalResultDiv = document.getElementById('optimalEmplacementResult');
            const emplacementIdInput = document.getElementById('emplacementIdInput');

            if (emplacementIdInput && emplacementIdInput.value === emplacementId && resultDisplayDivId === 'detailsEmplacement') {
                getEmplacementDetails();
            }
            else if (optimalResultDiv && optimalResultDiv.innerHTML.includes(emplacementId) && resultDisplayDivId === 'optimalEmplacementResult') {
                optimalResultDiv.innerHTML = "<p>L'emplacement précédemment suggéré a été libéré. Effectuez une nouvelle recherche.</p>";
                if (emplacementIdInput && emplacementIdInput.value === emplacementId) {
                    getEmplacementDetails();
                }
            }
            document.getElementById('assignationFormSection').classList.add('hidden');
        } else {
            if (resultTargetDiv) resultTargetDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${responseData.erreur || response.statusText}</p>`;
        }
    } catch (error) {
        console.error('Erreur lors de la libération:', error);
        if (resultTargetDiv) resultTargetDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur pour la libération.</p>`;
    }
}

async function submitBatchLiberation() {
    const idsTextarea = document.getElementById('batchLiberateIdsTextarea');
    const resultDiv = document.getElementById('batchLiberateResult');

    const idsString = idsTextarea.value.trim();
    if (!idsString) {
        resultDiv.innerHTML = '<p class="error-message">Veuillez entrer au moins un ID d_emplacement.</p>';
        return;
    }
    const idsList = idsString.split('\n').map(id => id.trim()).filter(id => id !== "");
    if (idsList.length === 0) {
        resultDiv.innerHTML = '<p class="error-message">Aucun ID d_emplacement valide fourni.</p>';
        return;
    }

    resultDiv.innerHTML = '<p>Libération en masse en cours...</p>';
    const payload = { ids_emplacements: idsList };

    try {
        const response = await fetch(`/api/emplacements/liberer-en-masse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const responseData = await response.json();

        if (response.ok && responseData.details) {
            let tableHtml = `<h3>Résultats de la Libération en Masse :</h3>`;
            if (responseData.message) {
                tableHtml += `<p class="info-message">${responseData.message}</p>`;
            }
            tableHtml += `<table class="stats-table resultats-batch-table"> 
                            <thead>
                                <tr>
                                    <th>Emplacement Cible</th>
                                    <th>Statut Final</th>
                                    <th>Ancien Produit Contenu</th>
                                    <th>Ancien ID Produit</th>
                                    <th>Détail</th>
                                </tr>
                            </thead>
                            <tbody>`;

            for (const id_emp_cible in responseData.details) {
                const detail = responseData.details[id_emp_cible];

                let statutAffichage = detail.status_final || detail.status;
                let messageAffichage = detail.message_final || detail.message_operation;

                switch (statutAffichage) {
                    case "LIBERE_SUCCES": statutAffichage = "Libéré avec succès"; break;
                    case "DEJA_LIBRE": statutAffichage = "Déjà libre"; break;
                    case "NON_TROUVE": statutAffichage = "Non trouvé"; break;
                    case "ERREUR_MARQUAGE": statutAffichage = "Erreur de marquage"; break;
                    case "ERREUR": statutAffichage = "Erreur interne"; break;
                    case "ECHEC_COMMIT": statutAffichage = "Échec (Rollback)"; break;
                    case "LIBERATION_NECESSAIRE": statutAffichage = "Prêt (non commité?)"; break;
                }

                tableHtml += `<tr>
                                  <td>${detail.id_emplacement_str}</td>
                                  <td>${statutAffichage}</td>
                                  <td>${detail.ancien_produit_nom || '-'}</td>
                                  <td>${detail.ancien_produit_id || '-'}</td>
                                  <td>${messageAffichage}</td>
                              </tr>`;
            }
            tableHtml += `</tbody></table>`;
            resultDiv.innerHTML = tableHtml;
            idsTextarea.value = '';
        } else if (responseData.erreur) {
            resultDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${responseData.erreur}</p>`;
        } else {
            resultDiv.innerHTML = `<p class="error-message">Réponse inattendue du serveur (Statut ${response.status}).</p>`;
        }
    } catch (error) {
        console.error('Erreur lors de la libération en masse:', error);
        resultDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur pour la libération en masse.</p>`;
    }
}

let produitsPourBatchAvecTailles = [];

async function processPastedProductsForSizeSpecification() {
    const productsTextarea = document.getElementById('batchAssignProductsTextarea');
    const specifySizesContainer = document.getElementById('specifySizesContainer');
    const resultDiv = document.getElementById('trueBatchAssignResult');


    resultDiv.innerHTML = "";
    specifySizesContainer.innerHTML = "";
    produitsPourBatchAvecTailles = [];

    const copyButton = document.getElementById('copyEmplacementsBtn');
    copyButton.classList.add('hidden');

    const productsString = productsTextarea.value.trim();
    if (!productsString) {
        resultDiv.innerHTML = '<p class="error-message">Veuillez coller les données des produits.</p>';
        return;
    }

    const lignesProduits = productsString.split('\n')
        .map(line => line.trim())
        .filter(line => line !== "");

    if (lignesProduits.length === 0) {
        resultDiv.innerHTML = '<p class="error-message">Aucune ligne de produit valide fournie.</p>';
        return;
    }

    let htmlGeneratedForSizes = '<table><tr><th>ID Produit</th><th>Nom Produit</th><th>Taille Requise</th></tr>';
    let parsingError = false;

    for (const [index, ligne] of lignesProduits.entries()) {
        const parts = ligne.split('\t').map(part => part.trim());
        if (parts.length < 2 || !parts[0] || !parts[1]) {
            resultDiv.innerHTML = `<p class="error-message">Ligne mal formatée : "${ligne}". Format attendu : ID_Produit [TAB] Nom_du_Produit</p>`;
            parsingError = true;
            break;
        }

        const id_produit = parts[0];
        const nom_produit = parts[1];

        produitsPourBatchAvecTailles.push({ id_produit, nom_produit });

        htmlGeneratedForSizes += `
            <tr>
                <td>${id_produit}</td>
                <td>${nom_produit}</td>
                <td>
                    <select id="taille_produit_${index}">
                        <option value="Petit">Petit</option>
                        <option value="Moyen" selected>Moyen</option>
                        <option value="Grand">Grand</option>
                    </select>
                </td>
            </tr>`;
    }
    htmlGeneratedForSizes += '</table>';

    if (parsingError) {
        produitsPourBatchAvecTailles = [];
        return;
    }

    if (produitsPourBatchAvecTailles.length > 0) {
        specifySizesContainer.innerHTML = htmlGeneratedForSizes;
        document.getElementById('batchAssignStep1').classList.add('hidden');
        document.getElementById('batchAssignStep2').classList.remove('hidden');
        resultDiv.innerHTML = "";
    } else {
        resultDiv.innerHTML = '<p class="error-message">Aucun produit à traiter après analyse.</p>';
    }
}

async function submitFinalBatchAssignProducts() {
    const resultDiv = document.getElementById('trueBatchAssignResult');
    const copyButton = document.getElementById('copyEmplacementsBtn');
    const exclureJ = document.getElementById('batchAssignExclureJ').checked;
    const eparpillementTotal = document.getElementById('trueBatchAssignEparpillementTotal').checked;

    if (produitsPourBatchAvecTailles.length === 0) {
        resultDiv.innerHTML = '<p class="error-message">Aucun produit n_a été préparé pour l_assignation. Veuillez d_abord valider les produits et spécifier les tailles.</p>';
        return;
    }

    const produits_payload = produitsPourBatchAvecTailles.map((prod, index) => {
        const tailleSelect = document.getElementById(`taille_produit_${index}`);
        return {
            id_produit: prod.id_produit,
            nom_produit: prod.nom_produit,
            taille_requise: tailleSelect ? tailleSelect.value : "Moyen"
        };
    });

    lastBatchAssignDetails = [];
    resultDiv.innerHTML = '<p>Assignation en masse en cours...</p>';

    const payloadAPI = {
        produits_a_assigner: produits_payload,
        exclure_allee_J: exclureJ,
        mode_eparpillage_total_global: eparpillementTotal
    };

    try {
        const response = await fetch(`/api/emplacements/assigner-en-masse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payloadAPI),
        });
        const responseData = await response.json();

        if (response.ok && responseData.details_assignations) {
            lastBatchAssignDetails = responseData.details_assignations;

            let tableHtml = `<h3>Résultats de l'Assignation en Masse :</h3>`;
            if (responseData.message) {
                tableHtml += `<p class="info-message">${responseData.message}</p>`;
            }
            tableHtml += `<table class="stats-table resultats-batch-table"> 
                            <thead>
                                <tr>
                                    <th>ID Produit Entrée</th>
                                    <th>Nom Produit Entrée</th>
                                    <th>Statut</th>
                                    <th>Emplacement Assigné</th>
                                    <th>Message/Détail</th>
                                </tr>
                            </thead>
                            <tbody>`;
            let hasSuccessfulAssignments = false;
            responseData.details_assignations.forEach(detail => {
                tableHtml += `<tr>
                                  <td>${detail.id_produit || 'N/A'}</td>
                                  <td>${detail.produit_nom || 'N/A'}</td>
                                  <td>${detail.statut}</td>
                                  <td>${detail.emplacement_assigne || '-'}</td>
                                  <td>${detail.message || ''}</td>
                              </tr>`;
                if (detail.statut === "Assigné" && detail.emplacement_assigne) {
                    hasSuccessfulAssignments = true;
                }
            });
            tableHtml += `</tbody></table>`;
            resultDiv.innerHTML = tableHtml;

            if (hasSuccessfulAssignments) {
                if (copyButton) {
                    copyButton.classList.remove('hidden');
                } else {
                    console.error("ERREUR JS: Le bouton avec l'ID 'copyEmplacementsBtn' est introuvable !");
                }
            }

            document.getElementById('batchAssignProductsTextarea').value = '';
            document.getElementById('specifySizesContainer').innerHTML = '';
            document.getElementById('batchAssignStep2').classList.add('hidden');
            document.getElementById('batchAssignStep1').classList.remove('hidden');
            produitsPourBatchAvecTailles = [];

        } else if (responseData.erreur) {
            resultDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${responseData.erreur}</p>`;
        } else {
            resultDiv.innerHTML = `<p class="error-message">Réponse inattendue du serveur (Statut ${response.status}).</p>`;
        }
    } catch (error) {
        console.error('Erreur lors de l_assignation en masse:', error);
        resultDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur pour l_assignation en masse.</p>`;
    }
}

function copyAssignedEmplacements() {
    const resultDiv = document.getElementById('trueBatchAssignResult');
    if (lastBatchAssignDetails.length === 0) {
        if (resultDiv) resultDiv.innerHTML += '<br><p class="error-message">Aucun résultat à copier.</p>';
        return;
    }

    const emplacementsText = lastBatchAssignDetails
        .map(detail => detail.emplacement_assigne || "")
        .join('\n');

    if (!emplacementsText.trim()) {
        if (resultDiv) resultDiv.innerHTML += '<br><p class="info-message">Aucun emplacement n_a été assigné dans ce lot.</p>';
        return;
    }

    navigator.clipboard.writeText(emplacementsText)
        .then(() => {
            if (resultDiv) resultDiv.innerHTML += '<br><p class="info-message" style="font-weight:bold;">Liste des emplacements assignés copiée dans le presse-papiers !</p>';
        })
        .catch(err => {
            console.error('Erreur lors de la copie dans le presse-papiers: ', err);
            if (resultDiv) resultDiv.innerHTML += '<br><p class="error-message">Erreur lors de la copie. Veuillez le faire manuellement.</p>';
        });
}


let donneesAlleeActuellementVisualisee = null;
function renderAlleeView(dataAllee, containerDiv) {
    if (!dataAllee || !containerDiv) {
        console.error("Données de l'allée ou conteneur manquant pour renderAlleeView.");
        if (containerDiv) containerDiv.innerHTML = "<p class='error-message'>Données de l'allée non disponibles.</p>";
        return;
    }

    containerDiv.innerHTML = "";

    if (dataAllee.racks_info && dataAllee.racks_info.length > 0) {

        let racksContainerHtml = '<div class="rack-container-scrollable">';
        dataAllee.racks_info.forEach(rack => {
            let currentRackHtml = `<div class="rack-view" id="rack-view-${rack.id_rack_complet_str}">`;
            currentRackHtml += `<h4>Rack ${rack.id_rack_complet_str}</h4>`;
            currentRackHtml += `<p class="rack-meta">Taille: ${rack.taille_emplacements_par_defaut} | ${rack.nombre_niveaux} Niveaux x ${rack.emplacements_par_niveau} Empl./Niveau</p>`;

            let gridHtml = `<div class="emplacements-grid" style="grid-template-columns: repeat(${rack.emplacements_par_niveau}, minmax(50px, 1fr));">`;

            let cells = {};
            for (let n = 1; n <= rack.nombre_niveaux; n++) {
                for (let p = 1; p <= rack.emplacements_par_niveau; p++) {
                    const current_id_str = `${rack.id_rack_complet_str}-${n}-${p}`;
                    cells[`${n}-${p}`] = `<div class="emplacement-cell" title="Vide ${current_id_str}" style="background-color:lightgrey; color:#555; font-style:italic;" onclick="handleEmplacementClick('${current_id_str}')">${current_id_str}</div>`;
                }
            }

            rack.emplacements.forEach(emp => {
                const estLibre = emp.est_libre;
                const classeStatut = estLibre ? 'libre' : 'occupe';
                const produitInfo = estLibre ? "Libre" : `${emp.produit_nom || 'Occupé'} (IDP: ${emp.produit_id || 'N/A'})`;
                const cellTitle = `Emplacement ${emp.id_emplacement_str} - ${produitInfo}`;

                let cellContent = "";
                if (estLibre) {
                    cellContent = emp.id_emplacement_str;
                } else {
                    if (emp.produit_nom) {
                        const maxChars = 20;
                        if (emp.produit_nom.length > maxChars) {
                            cellContent = emp.produit_nom.substring(0, maxChars) + "...";
                        } else {
                            cellContent = emp.produit_nom;
                        }
                    } else {
                        cellContent = "Occupé";
                    }
                }
                cells[`${emp.niveau}-${emp.position_dans_niveau}`] =
                    `<div class="emplacement-cell ${classeStatut}" title="${cellTitle}" onclick="handleEmplacementClick('${emp.id_emplacement_str}')">
                        ${cellContent}
                     </div>`;
            });
            for (let n = 1; n <= rack.nombre_niveaux; n++) {
                for (let p = 1; p <= rack.emplacements_par_niveau; p++) {
                    if (!cells[`${n}-${p}`]) {
                        const current_id_str = `${rack.id_rack_complet_str}-${n}-${p}`;
                        cells[`${n}-${p}`] =
                            `<div class="emplacement-cell vide-grille" title="Vide ${current_id_str}" onclick="handleEmplacementClick('${current_id_str}')">
                                ${current_id_str}
                             </div>`;
                    }
                }
            }

            for (let n = 1; n <= rack.nombre_niveaux; n++) {
                for (let p = 1; p <= rack.emplacements_par_niveau; p++) {
                    gridHtml += cells[`${n}-${p}`];
                }
            }
            gridHtml += `</div>`;

            currentRackHtml += gridHtml;
            currentRackHtml += `</div>`;

            racksContainerHtml += currentRackHtml;

        });

        racksContainerHtml += `</div>`;

        containerDiv.innerHTML = racksContainerHtml;

    } else {
        containerDiv.innerHTML = "<p>Aucun rack trouvé pour cette allée ou l'allée est vide.</p>";
    }
}

function handleEmplacementClick(idEmplacementStr, emplacementDetails = null) {
    console.log("Clic sur l'emplacement :", idEmplacementStr);

    let emplacementClique = emplacementDetails;

    if (!emplacementClique) {
        if (donneesAlleeActuellementVisualisee && donneesAlleeActuellementVisualisee.racks_info) {
            for (const rack of donneesAlleeActuellementVisualisee.racks_info) {
                emplacementClique = rack.emplacements.find(emp => emp.id_emplacement_str === idEmplacementStr);
                if (emplacementClique) break;
            }
        }
    }

    if (!emplacementClique) {
        console.error(`Détails non trouvés pour l'emplacement ${idEmplacementStr} ni dans les données actuelles ni en paramètre.`);
        alert(`Impossible d'obtenir les détails complets pour ${idEmplacementStr} pour une action directe.`);
        return;
    }

    modalTitle.textContent = `Action pour ${emplacementClique.id_emplacement_str}`;
    let contentHtml = '';
    if (emplacementClique.est_libre) {
        contentHtml = ` 
            <p>Cet emplacement est libre.</p>
            <div class="form-group">
                <label for="modalNomProduit">Nom du produit :</label>
                <input type="text" id="modalNomProduit" placeholder="Nom du produit" required>
            </div>
            <div class="form-group">
                <label for="modalIdProduit">ID du produit (obligatoire) :</label>
                <input type="text" id="modalIdProduit" placeholder="ID du produit" required>
            </div>
            <div class="modal-actions">
                <button class="btn-cancel" onclick="closeActionModal()">Annuler</button>
                <button onclick="doAssignFromModal('${emplacementClique.id_emplacement_str}')">Assigner</button>
            </div>
        `;
    } else {
        contentHtml = `
            <p>Emplacement occupé par : <strong>${emplacementClique.produit_nom || 'N/A'}</strong> (IDP: ${emplacementClique.produit_id || 'N/A'})</p>
            <p>Voulez-vous libérer cet emplacement ?</p>
            <div class="modal-actions">
                <button class="btn-cancel" onclick="closeActionModal()">Annuler</button>
                <button onclick="doLiberateFromModal('${emplacementClique.id_emplacement_str}')">Confirmer Libération</button>
            </div>
        `;
    }
    modalBodyContent.innerHTML = contentHtml;
    openActionModal();
}

async function chargerEtAfficherAllee(lettreAllee, targetRackNumero = null) {
    const planDetailsDiv = document.getElementById('detailsDeLAlleeAffichee');

    if (!planDetailsDiv) {
        console.error("ERREUR CRITIQUE: L'élément 'detailsDeLAlleeAffichee' est introuvable !");
        return;
    }

    planDetailsDiv.classList.remove('hidden');
    planDetailsDiv.innerHTML = `<p>Chargement des détails pour l'Allée ${lettreAllee}...</p>`;

    try {
        const response = await fetch(`/api/allees/${lettreAllee}/details`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ erreur: "Erreur non JSON du serveur." }));
            planDetailsDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${errorData.erreur || response.statusText}</p>`;
            setTimeout(() => { planDetailsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 50);
            return;
        }
        const dataAllee = await response.json();
        donneesAlleeActuellementVisualisee = dataAllee;

        planDetailsDiv.innerHTML = '';

        const titreAllee = document.createElement('h2');
        titreAllee.textContent = `Détails de l'Allée ${dataAllee.lettre_allee}`;
        planDetailsDiv.appendChild(titreAllee);

        const vizContainer = document.createElement('div');
        vizContainer.id = 'visualisationAlleeConteneur';
        vizContainer.style.marginTop = '20px';
        vizContainer.style.overflowX = 'auto';
        planDetailsDiv.appendChild(vizContainer);

        renderAlleeView(dataAllee, vizContainer);

        if (targetRackNumero !== null && dataAllee.racks_info && dataAllee.racks_info.length > 0) {
            const targetRackDomId = `rack-view-${lettreAllee}${targetRackNumero}`;
            const targetRackElement = document.getElementById(targetRackDomId);

            if (targetRackElement) {
                setTimeout(() => {
                    targetRackElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'nearest',
                        inline: 'start'
                    });
                    targetRackElement.style.transition = 'outline 0.2s ease-in-out';
                    targetRackElement.style.outline = '3px solid #e75f44';
                    setTimeout(() => {
                        targetRackElement.style.outline = 'none';
                    }, 2500);
                }, 100);
            } else {
                console.warn(`Le rack avec l'ID DOM '${targetRackDomId}' n'a pas été trouvé pour le défilement horizontal.`);
            }
        }


        setTimeout(() => {
            if (titreAllee) {
                titreAllee.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }, 150);

    } catch (error) {
        console.error(`Erreur lors du chargement de l'allée ${lettreAllee}:`, error);
        if (planDetailsDiv) {
            planDetailsDiv.innerHTML = `<p class="error-message">Impossible de charger les détails de l'allée. Erreur de communication.</p>`;
            setTimeout(() => { planDetailsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 50);
        }
    }
}

async function submitRechercheProduit() {
    const terme = document.getElementById('termeRechercheProduitInput').value;
    const resultDiv = document.getElementById('resultatsRechercheProduit');

    if (!terme || terme.length < 2) {
        resultDiv.innerHTML = '<p class="error-message">Veuillez entrer au moins 2 caractères pour la recherche.</p>';
        return;
    }

    resultDiv.innerHTML = `<p>Recherche du produit '${terme}' en cours...</p>`;

    try {
        const response = await fetch(`/api/produits/rechercher?q=${encodeURIComponent(terme)}`);
        const data = await response.json();

        if (response.ok) {
            if (data && data.length > 0) {
                let tableHtml = `<h3>Produits trouvés pour '${terme}' :</h3>`;
                tableHtml += `<table class="stats-table search-results-table"> 
                                <thead>
                                    <tr>
                                        <th>ID Produit</th>
                                        <th>Nom Produit</th>
                                        <th>Emplacement</th> 
                                        </tr>
                                </thead>
                                <tbody>`;

                data.forEach(emp => {
                    tableHtml += `<tr>
                                      <td>${emp.produit_id || 'N/A'}</td>
                                      <td>${emp.produit_nom || 'N/A'}</td>
                                      <td>${emp.id_emplacement_str || 'N/A'}</td>
                                  </tr>`;
                });
                tableHtml += `</tbody></table>`;
                resultDiv.innerHTML = tableHtml;
            } else {
                resultDiv.innerHTML = `<p class="info-message">Aucun produit trouvé pour '${terme}'.</p>`;
            }
        } else {
            resultDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${data.erreur || 'Erreur lors de la recherche.'}</p>`;
        }
    } catch (error) {
        console.error('Erreur lors de la recherche de produit:', error);
        resultDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur pour la recherche de produit.</p>`;
    }
}

async function chargerStatistiques() {
    const resultDiv = document.getElementById('resultatsStatistiques');
    resultDiv.innerHTML = '<p>Chargement des statistiques...</p>';

    try {
        const response = await fetch('/api/entrepot/statistiques');
        const data = await response.json();

        if (response.ok) {
            if (data.erreur) {
                resultDiv.innerHTML = `<p class="error-message">${data.erreur}</p>`;
                return;
            }

            let htmlResult = `<h3>Statistiques Globales</h3>`;
            htmlResult += `<ul>
                                <li>Total Emplacements : <strong>${data.total_emplacements || 0}</strong></li>
                                <li>Emplacements Occupés : <strong>${data.emplacements_occupes || 0}</strong></li>
                                <li>Emplacements Libres : <strong>${data.emplacements_libres || 0}</strong></li>
                                <li>Dont Hauts (Niv 1-7) : <strong>${data.emplacements_hauts_libres_global || 0}</strong></li>
                                <li>Taux d'Occupation Global : <strong>${data.taux_occupation_global || 0}%</strong></li>
                           </ul>`;

            if (data.par_taille && Object.keys(data.par_taille).length > 0) {
                htmlResult += `<h3>Détail par Taille d'Emplacement</h3>`;
                htmlResult += `<table class="stats-table">
                                <thead><tr><th>Taille</th><th>Total</th><th>Occupés</th><th>Libres</th><th>Taux Occ.</th><th>Total Hauts</th><th>Occupés Hauts</th><th>Libres Hauts</th><th>Taux Occ. Hauts</th></tr></thead>
                                <tbody>`;
                const taillesOrdonnees = Object.keys(data.par_taille).sort(/* ... */);
                for (const taille of taillesOrdonnees) {
                    const statsTaille = data.par_taille[taille];
                    htmlResult += `<tr>
                                       <td>${taille}</td>
                                       <td>${statsTaille.total}</td>
                                       <td>${statsTaille.occupes}</td>
                                       <td>${statsTaille.libres}</td>
                                       <td>${statsTaille.taux_occupation}%</td>
                                       <td>${statsTaille.total_hauts || 0}</td>    
                                       <td>${statsTaille.occupes_hauts || 0}</td>   
                                       <td>${statsTaille.libres_hauts || 0}</td>    
                                       <td>${statsTaille.taux_occupation_hauts || 0}%</td> 
                                    </tr>`;
                }
                htmlResult += `</tbody></table>`;
            }

            if (data.par_allee && Object.keys(data.par_allee).length > 0) {
                htmlResult += `<h3>Détail par Allée</h3>`;
                htmlResult += `<table class="stats-table">
                                <thead><tr><th>Allée</th><th>Total Empl.</th><th>Occupés</th><th>Libres</th><th>Taux Occ.</th><th>Total Hauts</th><th>Occupés Hauts</th><th>Libres Hauts</th><th>Taux Occ. Hauts</th></tr></thead>
                                <tbody>`;
                const sortedAllees = Object.keys(data.par_allee).sort();
                for (const lettreAllee of sortedAllees) {
                    const statsAllee = data.par_allee[lettreAllee];
                    htmlResult += `<tr>
                                       <td>${lettreAllee}</td>
                                       <td>${statsAllee.total}</td>
                                       <td>${statsAllee.occupes}</td>
                                       <td>${statsAllee.libres}</td>
                                       <td>${statsAllee.taux_occupation}%</td>
                                       <td>${statsAllee.total_hauts || 0}</td>
                                       <td>${statsAllee.occupes_hauts || 0}</td>
                                       <td>${statsAllee.libres_hauts || 0}</td>     
                                       <td>${statsAllee.taux_occupation_hauts || 0}%</td>  
                                    </tr>`;
                }
                htmlResult += `</tbody></table>`;
            }
            resultDiv.innerHTML = htmlResult;
        } else {
            resultDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${data.erreur || 'Erreur lors du chargement des statistiques.'}</p>`;
        }
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
        resultDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur pour les statistiques.</p>`;
    }
}


// Historique //
let historiquePageActuelle = 1;
const historiqueElementsParPage = 15;

async function chargerHistorique(page = 1) {
    historiquePageActuelle = page;
    const resultDiv = document.getElementById('resultatsHistorique');
    const paginationDiv = document.getElementById('paginationHistorique');
    resultDiv.innerHTML = '<p>Chargement de l_historique...</p>';
    paginationDiv.innerHTML = '';

    const typeAction = document.getElementById('histTypeAction').value;
    const idEmplacement = document.getElementById('histIdEmplacement').value;
    const idProduit = document.getElementById('histIdProduit').value;

    let queryParams = new URLSearchParams({
        page: historiquePageActuelle,
        par_page: historiqueElementsParPage
    });
    if (typeAction) queryParams.append('type_action', typeAction);
    if (idEmplacement) queryParams.append('id_emplacement', idEmplacement);
    if (idProduit) queryParams.append('id_produit', idProduit);

    try {
        const response = await fetch(`/api/historique?${queryParams.toString()}`);
        const data = await response.json();

        if (response.ok) {
            if (data.erreur) {
                resultDiv.innerHTML = `<p class="error-message">${data.erreur}</p>`;
                return;
            }

            if (data.mouvements && data.mouvements.length > 0) {
                let htmlResult = `<table class="stats-table">
                                    <thead><tr><th>Date/Heure</th><th>Action</th><th>Emplacement</th><th>ID Produit</th><th>Nom Produit</th><<th>Utilisateur</th>/tr></thead>
                                    <tbody>`;
                data.mouvements.forEach(m => {
                    htmlResult += `<tr>
                                       <td>${m.timestamp}</td>
                                       <td>${m.type_action}</td>
                                       <td>${m.id_emplacement_str}</td>
                                       <td>${m.produit_id || '-'}</td>
                                       <td>${m.produit_nom || '-'}</td>
                                       <td>${m.utilisateur_nom || 'N/A'}</td>
                                    </tr>`;
                });
                htmlResult += `</tbody></table>`;
                resultDiv.innerHTML = htmlResult;
                renderPaginationHistorique(data.pagination);
            } else {
                resultDiv.innerHTML = `<p class="info-message">Aucun mouvement trouvé pour les critères actuels.</p>`;
            }
        } else {
            resultDiv.innerHTML = `<p class="error-message">Erreur ${response.status}: ${data.erreur || 'Erreur lors du chargement de l_historique.'}</p>`;
        }
    } catch (error) {
        console.error('Erreur lors du chargement de l_historique:', error);
        resultDiv.innerHTML = `<p class="error-message">Impossible de contacter le serveur pour l_historique.</p>`;
    }
}

function renderPaginationHistorique(paginationData) {
    const paginationDiv = document.getElementById('paginationHistorique');
    if (!paginationData || paginationData.total_pages <= 1) {
        paginationDiv.innerHTML = '';
        return;
    }

    let paginationHtml = '';
    if (paginationData.page_actuelle > 1) {
        paginationHtml += `<button onclick="chargerHistorique(${paginationData.page_actuelle - 1})">&laquo; Précédent</button> `;
    }

    paginationHtml += ` Page ${paginationData.page_actuelle} sur ${paginationData.total_pages} `;

    if (paginationData.page_actuelle < paginationData.total_pages) {
        paginationHtml += `<button onclick="chargerHistorique(${paginationData.page_actuelle + 1})">Suivant &raquo;</button>`;
    }
    paginationDiv.innerHTML = paginationHtml;
}


const modalOverlay = document.getElementById('actionEmplacementModalOverlay');
const actionModal = document.getElementById('actionEmplacementModal');
const modalTitle = document.getElementById('modalTitle');
const modalBodyContent = document.getElementById('modalBodyContent');

function openActionModal() {
    modalOverlay.classList.remove('hidden');
    actionModal.classList.remove('hidden');
}

function closeActionModal() {
    modalOverlay.classList.add('hidden');
    actionModal.classList.add('hidden');
    modalBodyContent.innerHTML = '';
}

async function assignerProduitViaPlan(idEmplacement, nomProduit, idProduit) {
    const payload = { nom_produit: nomProduit };
    if (idProduit) payload.id_produit = idProduit;

    const db_session = null;

    showTemporaryMessageInPlanDetails(`Assignation de '${nomProduit}' à ${idEmplacement} en cours...`);

    try {
        const response = await fetch(`/api/emplacements/${idEmplacement}/assigner`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const responseData = await response.json();
        if (response.ok) {
            showTemporaryMessageInPlanDetails(`Produit assigné ! Actualisation de la vue...`, 'info-message');
            if (donneesAlleeActuellementVisualisee) {
                chargerEtAfficherAllee(donneesAlleeActuellementVisualisee.lettre_allee);
            }
        } else {
            showTemporaryMessageInPlanDetails(`Erreur d'assignation: ${responseData.erreur || response.statusText}`, 'error-message');
        }
    } catch (error) {
        console.error("Erreur API assignation via plan:", error);
        showTemporaryMessageInPlanDetails("Erreur communication serveur pour assignation.", 'error-message');
    }
}

async function libererEmplacementViaPlan(idEmplacement) {
    showTemporaryMessageInPlanDetails(`Libération de ${idEmplacement} en cours...`);
    try {
        const response = await fetch(`/api/emplacements/${idEmplacement}/liberer`, { method: 'POST' });
        const responseData = await response.json();
        if (response.ok) {
            showTemporaryMessageInPlanDetails(`Emplacement libéré ! Actualisation de la vue...`, 'info-message');
            if (donneesAlleeActuellementVisualisee) {
                chargerEtAfficherAllee(donneesAlleeActuellementVisualisee.lettre_allee);
            }
        } else {
            showTemporaryMessageInPlanDetails(`Erreur de libération: ${responseData.erreur || response.statusText}`, 'error-message');
        }
    } catch (error) {
        console.error("Erreur API libération via plan:", error);
        showTemporaryMessageInPlanDetails("Erreur communication serveur pour libération.", 'error-message');
    }
}

function showTemporaryMessageInPlanDetails(message, messageClass = '') {
    const detailsDiv = document.getElementById('detailsDeLAlleeAffichee');
    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    if (messageClass) messageElement.className = messageClass;
    detailsDiv.insertBefore(messageElement, detailsDiv.firstChild);
    setTimeout(() => {
        if (messageElement.parentNode === detailsDiv) {
            detailsDiv.removeChild(messageElement);
        }
    }, 4000);
}

async function doAssignFromModal(idEmplacement) {
    const nomProduit = document.getElementById('modalNomProduit').value;
    const idProduit = document.getElementById('modalIdProduit').value;

    if (!nomProduit || !idProduit) {
        alert("Le nom et l'ID du produit sont obligatoires.");
        return;
    }

    closeActionModal();
    showTemporaryMessageInPlanDetails(`Assignation de '${nomProduit}' à ${idEmplacement} en cours...`);
    await assignerProduitViaPlan(idEmplacement, nomProduit, idProduit);
}

async function doLiberateFromModal(idEmplacement) {
    closeActionModal();
    showTemporaryMessageInPlanDetails(`Libération de ${idEmplacement} en cours...`);
    await libererEmplacementViaPlan(idEmplacement);
}


async function chargerStatistiquesAccueil() {
    const kpiContainer = document.getElementById('accueilStatsKPIs');
    if (!kpiContainer) return;

    kpiContainer.innerHTML = '<p>Chargement des indicateurs...</p>';

    try {
        const response = await fetch('/api/entrepot/statistiques');
        const data = await response.json();

        if (response.ok && !data.erreur) {
            let kpiHtml = '';

            kpiHtml += `<div class="kpi-card">
                            <span class="kpi-value">${data.taux_occupation_global || 0}%</span>
                            <span class="kpi-label">Taux d'Occupation Global</span>
                        </div>`;

            kpiHtml += `<div class="kpi-card">
                            <span class="kpi-value">${data.emplacements_libres || 0}</span>
                            <span class="kpi-label">Emplacements Libres</span>
                        </div>`;

            kpiHtml += `<div class="kpi-card">
                            <span class="kpi-value">${data.emplacements_hauts_libres_global || 0}</span>
                            <span class="kpi-label">Emplacements Hauts Libres</span>
                        </div>`;

            kpiContainer.innerHTML = kpiHtml;
        } else {
            kpiContainer.innerHTML = `<p class="error-message">Erreur chargement stats: ${data.erreur || 'Réponse invalide'}</p>`;
        }
    } catch (error) {
        console.error('Erreur fetch stats accueil:', error);
        kpiContainer.innerHTML = `<p class="error-message">Impossible de charger les indicateurs clés.</p>`;
    }
}

function reorderWarehousePlanForMobile() {
    const mobileBreakpoint = 1460;
    const planWrapper = document.querySelector('#sectionPlan .plan-entrepot-wrapper-avec-zones');

    if (!planWrapper) {
        console.error("Conteneur du plan (.plan-entrepot-wrapper-avec-zones) non trouvé.");
        return;
    }

    const aisleElements = Array.from(planWrapper.querySelectorAll('[data-aisle-main]'));

    if (window.innerWidth <= mobileBreakpoint) {
        if (!planWrapper.classList.contains('mobile-plan-sorted')) {
            console.log("Application de l'ordre mobile pour le plan.");

            const sortedAisles = aisleElements.sort((a, b) => {
                const mainA = a.dataset.aisleMain;
                const mainB = b.dataset.aisleMain;
                const subA = parseInt(a.dataset.aisleSub, 10);
                const subB = parseInt(b.dataset.aisleSub, 10);

                if (mainA < mainB) return -1;
                if (mainA > mainB) return 1;
                return subA - subB;
            });

            aisleElements.forEach(el => el.remove());

            sortedAisles.forEach(el => {
                planWrapper.appendChild(el);
            });

            planWrapper.classList.add('mobile-plan-sorted');
            planWrapper.classList.remove('desktop-plan-sorted');
        }
    } else {
        if (planWrapper.classList.contains('mobile-plan-sorted')) {
            console.log("Restauration de l'ordre bureau pour le plan (rechargement).");
            window.location.reload();

            planWrapper.classList.remove('mobile-plan-sorted');
            planWrapper.classList.add('desktop-plan-sorted');
        }
    }
}

function debounce(func, wait, immediate) {
    var timeout;
    return function () {
        var context = this, args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
};
window.addEventListener('DOMContentLoaded', reorderWarehousePlanForMobile);
window.addEventListener('resize', debounce(reorderWarehousePlanForMobile, 250));
